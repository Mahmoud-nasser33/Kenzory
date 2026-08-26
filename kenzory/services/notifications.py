"""Notification service — create, query, and deliver in-app + email alerts."""

import logging
from datetime import datetime

from flask import render_template, url_for
from flask_mail import Message

from kenzory.extensions import db, mail
from kenzory.models.notification import (
    TYPE_BADGE_EARNED,
    TYPE_ENDORSEMENT_RECEIVED,
    TYPE_REVIEW_RECEIVED,
    TYPE_SUBMISSION_APPROVED,
    TYPE_SUBMISSION_REJECTED,
    Notification,
)

log = logging.getLogger(__name__)

EMAIL_SUBJECTS = {
    TYPE_SUBMISSION_APPROVED: "Your submission was approved!",
    TYPE_SUBMISSION_REJECTED: "Update on your submission",
    TYPE_REVIEW_RECEIVED: "New review on your heritage place",
    TYPE_ENDORSEMENT_RECEIVED: "Someone endorsed your submission",
    TYPE_BADGE_EARNED: "You earned a new badge!",
}


def create_notification(user_id, type, title, message, link=None):
    """Persist an in-app notification and attempt email delivery."""
    notif = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        link=link,
        created_at=datetime.utcnow(),
    )
    db.session.add(notif)
    db.session.flush()
    _send_email(notif)
    return notif


def unread_count(user_id):
    """Return the number of unread notifications for a user."""
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()


def recent_notifications(user_id, limit=20):
    """Newest-first notifications for the dropdown / page."""
    return (
        Notification.query.filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )


def all_notifications(user_id, page=1, per_page=20):
    """Paginated notifications for the notifications page."""
    return db.paginate(
        Notification.query.filter_by(user_id=user_id).order_by(
            Notification.created_at.desc()
        ),
        page=page,
        per_page=per_page,
        error_out=False,
    )


def mark_read(notification_id, user_id):
    """Mark a single notification as read (only if owned by user)."""
    notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if notif and not notif.is_read:
        notif.is_read = True
        db.session.flush()
    return notif


def mark_all_read(user_id):
    """Mark every unread notification for a user as read."""
    Notification.query.filter_by(user_id=user_id, is_read=False).update(
        {"is_read": True}
    )
    db.session.flush()


# ---------------------------------------------------------------------------
# High-level helpers called from route / service code
# ---------------------------------------------------------------------------


def notify_submission_approved(place, submitter):
    """Notify the contributor that their submission was approved."""
    link = url_for("places.place_detail", slug=place.slug, _external=False)
    create_notification(
        user_id=submitter.id,
        type=TYPE_SUBMISSION_APPROVED,
        title="Your submission was approved!",
        message=f'"{place.title}" is now live on Kenzory.',
        link=link,
    )


def notify_submission_rejected(submission, reviewer_note=None):
    """Notify the contributor that their submission was rejected."""
    msg = "The review team decided not to publish this submission."
    if reviewer_note:
        msg += f" Note from reviewer: {reviewer_note}"
    create_notification(
        user_id=submission.submitted_by,
        type=TYPE_SUBMISSION_REJECTED,
        title="Update on your submission",
        message=msg,
        link=url_for("contributions.my_submissions", _external=False),
    )


def notify_review_received(place, reviewer):
    """Notify the place creator that someone left a review."""
    link = url_for("places.place_detail", slug=place.slug, _external=False) + "#reviews"
    create_notification(
        user_id=place.created_by,
        type=TYPE_REVIEW_RECEIVED,
        title="New review on your place",
        message=f'{reviewer.display} reviewed "{place.title}".',
        link=link,
    )


def notify_endorsement_received(submission, endorser):
    """Notify the submitter that someone endorsed their submission."""
    create_notification(
        user_id=submission.submitted_by,
        type=TYPE_ENDORSEMENT_RECEIVED,
        title="New endorsement",
        message=f"{endorser.display} endorsed your submission.",
        link=url_for("contributions.community_review", _external=False),
    )


def notify_badge_earned(user, badge_name):
    """Notify a user that they earned a new badge."""
    create_notification(
        user_id=user.id,
        type=TYPE_BADGE_EARNED,
        title="New badge earned!",
        message=f'You earned the "{badge_name}" badge.',
        link=url_for("profile.profile", _external=False),
    )


# ---------------------------------------------------------------------------
# Email delivery (best-effort, never blocks the request)
# ---------------------------------------------------------------------------


def _send_email(notif):
    """Attempt to send an email for the notification. Catches all errors."""
    try:
        from flask import current_app

        if current_app.config.get("MAIL_SUPPRESS_SEND"):
            return
        if not notif.user or not notif.user.email:
            return

        subject = EMAIL_SUBJECTS.get(notif.type, "Kenzory notification")
        msg = Message(subject=subject, recipients=[notif.user.email])
        msg.html = render_template(
            "emails/notification.html",
            notification=notif,
            user=notif.user,
        )
        msg.body = notif.message
        mail.send(msg)
    except Exception:
        log.exception("Failed to send notification email (notif id=%s)", notif.id)
