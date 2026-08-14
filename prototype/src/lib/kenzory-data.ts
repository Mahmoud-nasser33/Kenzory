import mosque from "@/assets/place-mosque.jpg";
import railway from "@/assets/place-railway.jpg";
import coptic from "@/assets/place-coptic.jpg";
import nubian from "@/assets/place-nubian.jpg";
import temple from "@/assets/place-temple.jpg";
import palace from "@/assets/place-palace.jpg";

export const images = { mosque, railway, coptic, nubian, temple, palace };

export type Verification = "official" | "community" | "review" | "unverified";

export const verificationMeta: Record<
  Verification,
  { label: string; tone: string; dot: string }
> = {
  official: {
    label: "Officially Verified",
    tone: "text-[color:var(--verified)] border-[color:var(--verified)]/30 bg-[color:var(--verified)]/10",
    dot: "bg-[color:var(--verified)]",
  },
  community: {
    label: "Community Verified",
    tone: "text-[color:var(--community)] border-[color:var(--community)]/30 bg-[color:var(--community)]/10",
    dot: "bg-[color:var(--community)]",
  },
  review: {
    label: "Under Review",
    tone: "text-[color:var(--gold-foreground)] border-[color:var(--review)]/50 bg-[color:var(--review)]/20",
    dot: "bg-[color:var(--review)]",
  },
  unverified: {
    label: "Unverified",
    tone: "text-muted-foreground border-border bg-muted",
    dot: "bg-[color:var(--unverified)]",
  },
};

export const categories = [
  "Ancient Egyptian",
  "Islamic Heritage",
  "Coptic Heritage",
  "Ottoman",
  "Modern Egyptian History",
  "Traditional Architecture",
  "Cultural Heritage",
  "Unknown / Local Heritage",
] as const;

export type Category = (typeof categories)[number];

export const periods = [
  "Pharaonic",
  "Greco-Roman",
  "Coptic Era",
  "Early Islamic",
  "Mamluk",
  "Ottoman Period",
  "Khedivial Era",
  "Modern (20th c.)",
] as const;

export const governorates = [
  "Cairo",
  "Giza",
  "Alexandria",
  "Minya",
  "Asyut",
  "Sohag",
  "Qena",
  "Luxor",
  "Aswan",
  "Fayoum",
  "Beni Suef",
  "Beheira",
  "Sharqia",
  "Dakahlia",
  "Gharbia",
  "Port Said",
  "Ismailia",
  "Suez",
  "Matrouh",
  "New Valley",
  "Red Sea",
  "North Sinai",
  "South Sinai",
  "Damietta",
  "Kafr El Sheikh",
  "Monufia",
  "Qalyubia",
];

export type Place = {
  id: string;
  name: string;
  nameAr: string;
  governorate: string;
  city: string;
  category: Category;
  period: string;
  approxDate: string;
  verification: Verification;
  distanceKm: number;
  visitMinutes: number;
  image: string;
  gallery: string[];
  lat: number;
  lng: number;
  summary: string;
  description: string;
  whyItMatters: string;
  architecture: string[];
  timeline: { year: string; event: string }[];
  stories: { title: string; author: string; text: string }[];
  sources: { label: string; type: string }[];
  contributor: { name: string; level: string; initials: string };
  addedAgo: string;
  saves: number;
  photos: number;
};

export const places: Place[] = [
  {
    id: "mosque-al-hamawi",
    name: "Historic Mosque of Al-Hamawi",
    nameAr: "مسجد الحماوي الأثري",
    governorate: "Minya",
    city: "Mallawi",
    category: "Islamic Heritage",
    period: "Ottoman Period",
    approxDate: "c. 1710 CE",
    verification: "official",
    distanceKm: 12,
    visitMinutes: 45,
    image: mosque,
    gallery: [mosque, palace, nubian],
    lat: 27.73,
    lng: 30.84,
    summary:
      "A modest Ottoman village mosque with an unusual tapered minaret, largely absent from tourism maps.",
    description:
      "Built during the early Ottoman administration of Middle Egypt, the mosque served a farming community along a since-diverted canal branch. Its prayer hall combines a square domed chamber with a low arcaded portico built from reused limestone blocks, a common practice in Middle Egyptian villages where older structures supplied building material.",
    whyItMatters:
      "It is one of very few surviving provincial Ottoman mosques in Minya that retains its original minaret profile. Provincial religious architecture is heavily under-documented compared to Cairo's monuments, making each surviving example significant for understanding how imperial styles were adapted locally.",
    architecture: [
      "Tapered cylindrical minaret with a ribbed cap",
      "Square domed prayer chamber on squinches",
      "Reused Greco-Roman limestone in the foundations",
      "Carved wooden minbar (partially restored, 1998)",
    ],
    timeline: [
      { year: "c. 1710", event: "Mosque founded by a local grain merchant family." },
      { year: "1867", event: "Portico added; canal-side entrance relocated." },
      { year: "1998", event: "Partial restoration of the minbar and roof timbers." },
      { year: "2021", event: "Listed in a regional heritage survey." },
    ],
    stories: [
      {
        title: "The Friday everyone walked from the next village",
        author: "Om Sabah, 71",
        text: "Demo content. Villagers recall that before the newer mosque was built in the 1980s, families from three hamlets walked here every Friday along the canal path.",
      },
    ],
    sources: [
      { label: "Ministry of Tourism and Antiquities regional listing", type: "Official record" },
      { label: "Survey of Provincial Ottoman Mosques, Cairo Univ.", type: "Academic" },
      { label: "Local endowment (waqf) documents", type: "Archive" },
    ],
    contributor: { name: "Mahmoud", level: "Heritage Explorer", initials: "M" },
    addedAgo: "2 days ago",
    saves: 214,
    photos: 23,
  },
  {
    id: "station-nag-hammadi",
    name: "Abandoned Railway Station of Deir Sharaf",
    nameAr: "محطة سكة حديد دير شرف المهجورة",
    governorate: "Sohag",
    city: "Tahta",
    category: "Modern Egyptian History",
    period: "Khedivial Era",
    approxDate: "c. 1903 CE",
    verification: "community",
    distanceKm: 24,
    visitMinutes: 60,
    image: railway,
    gallery: [railway, palace, mosque],
    lat: 26.77,
    lng: 31.5,
    summary:
      "A cast-iron and timber station hall from the sugar-line expansion, closed since the 1970s.",
    description:
      "Constructed during the expansion of the Upper Egypt sugar railway, the station once handled cane freight and passenger traffic for surrounding villages. The hall's imported iron trusses and arched fenestration reflect the standardised khedivial-era station typology deployed along the Nile Valley.",
    whyItMatters:
      "Industrial heritage in Egypt is rarely protected. Stations like this document the country's early industrial modernity and the social history of rural mobility, yet most are demolished without record.",
    architecture: [
      "Imported riveted iron roof trusses",
      "Repeating arched windows with fanlights",
      "Original blue-and-cream painted dado",
      "Surviving in-floor track section",
    ],
    timeline: [
      { year: "1903", event: "Opened as a freight halt on the sugar line." },
      { year: "1932", event: "Passenger platform and ticket hall added." },
      { year: "1974", event: "Service discontinued after line rerouting." },
      { year: "2024", event: "Documented by Kenzory contributors." },
    ],
    stories: [
      {
        title: "The stationmaster's last logbook",
        author: "Ahmed R.",
        text: "Demo content. A retired employee's family still keeps the final logbook, its last entry dated the week the line closed.",
      },
    ],
    sources: [
      { label: "Egyptian National Railways historical timetables", type: "Archive" },
      { label: "Community photo documentation, 2024", type: "Community" },
    ],
    contributor: { name: "Ahmed", level: "Field Documenter", initials: "A" },
    addedAgo: "5 days ago",
    saves: 168,
    photos: 41,
  },
  {
    id: "deir-al-qusayr",
    name: "Cliff Monastery of Deir al-Qusayr",
    nameAr: "دير القصير في الجبل",
    governorate: "Asyut",
    city: "Abnub",
    category: "Coptic Heritage",
    period: "Coptic Era",
    approxDate: "5th–6th century CE",
    verification: "official",
    distanceKm: 31,
    visitMinutes: 90,
    image: coptic,
    gallery: [coptic, temple, mosque],
    lat: 27.27,
    lng: 31.15,
    summary:
      "Rock-cut monastic cells and a courtyard church carved into the eastern desert escarpment.",
    description:
      "A monastic settlement cut directly into the limestone cliff, with communal cells arranged around an open court. Faint traces of painted plaster survive in two chambers. The site remained in seasonal use into the modern period and is still visited during local feast days.",
    whyItMatters:
      "The site preserves an early monastic plan rarely visible elsewhere, and it remains a living place of local devotion — a case where archaeological value and continuing community use overlap.",
    architecture: [
      "Rock-cut cells with carved niches",
      "Open courtyard church with three crosses",
      "Remains of painted plaster (unstudied)",
      "Cistern system fed by winter runoff",
    ],
    timeline: [
      { year: "5th c.", event: "First cells cut into the cliff face." },
      { year: "11th c.", event: "Courtyard church enlarged." },
      { year: "1900s", event: "Seasonal use by nearby village families." },
      { year: "2019", event: "Condition survey recorded surface erosion." },
    ],
    stories: [
      {
        title: "Feast day at the cliff",
        author: "Mariam G.",
        text: "Demo content. Families climb the path before dawn once a year, carrying bread baked the night before.",
      },
    ],
    sources: [
      { label: "Ministry of Tourism and Antiquities site file", type: "Official record" },
      { label: "Coptic Monastic Archaeology (academic paper)", type: "Academic" },
    ],
    contributor: { name: "Mariam", level: "Senior Documenter", initials: "M" },
    addedAgo: "1 week ago",
    saves: 302,
    photos: 57,
  },
  {
    id: "nubian-house-gharb-soheil",
    name: "Painted Nubian House, West Bank",
    nameAr: "بيت نوبي مزخرف بالضفة الغربية",
    governorate: "Aswan",
    city: "Gharb Soheil",
    category: "Traditional Architecture",
    period: "Modern (20th c.)",
    approxDate: "c. 1930s",
    verification: "community",
    distanceKm: 8,
    visitMinutes: 30,
    image: nubian,
    gallery: [nubian, coptic, temple],
    lat: 24.05,
    lng: 32.87,
    summary:
      "A vaulted mudbrick house with hand-painted geometric bands, built before the resettlement era.",
    description:
      "The house uses load-bearing mudbrick with a shallow dome over the main room, a construction technique tuned to extreme heat. The painted bands, renewed by successive generations, encode family and regional motifs rather than purely decorative patterns.",
    whyItMatters:
      "Pre-resettlement Nubian domestic architecture is disappearing rapidly. Documenting surviving houses preserves both building knowledge and the visual vocabulary of a displaced community.",
    architecture: [
      "Load-bearing mudbrick with shallow dome",
      "Hand-painted geometric bands renewed by family",
      "Deep-set doorways for shade",
      "Palm-trunk roof beams",
    ],
    timeline: [
      { year: "1930s", event: "House built by the current family's grandfather." },
      { year: "1964", event: "Motifs repainted after relatives resettled here." },
      { year: "2023", event: "Photographed for community documentation." },
    ],
    stories: [
      {
        title: "Why the band above the door is never repainted",
        author: "Sayed N.",
        text: "Demo content. One band is deliberately left untouched — the family treats it as the grandmother's signature.",
      },
    ],
    sources: [{ label: "Community documentation, 2023", type: "Community" }],
    contributor: { name: "Sayed", level: "Heritage Explorer", initials: "S" },
    addedAgo: "3 days ago",
    saves: 96,
    photos: 18,
  },
  {
    id: "buried-temple-fayoum",
    name: "Partially Buried Temple Terrace",
    nameAr: "شرفة معبد مطمورة جزئياً",
    governorate: "Fayoum",
    city: "Qasr Qarun area",
    category: "Ancient Egyptian",
    period: "Greco-Roman",
    approxDate: "c. 1st century BCE",
    verification: "review",
    distanceKm: 46,
    visitMinutes: 75,
    image: temple,
    gallery: [temple, coptic, railway],
    lat: 29.4,
    lng: 30.42,
    summary:
      "An exposed colonnaded terrace at the desert edge, reported by local guides and awaiting assessment.",
    description:
      "Wind erosion has exposed part of a limestone colonnade at the desert margin. The visible fragments suggest a Greco-Roman phase, though no excavation report is publicly available and the identification remains provisional.",
    whyItMatters:
      "If confirmed, the terrace would extend the known settlement footprint at the lake's western edge. Kenzory presents it as reported, not established.",
    architecture: [
      "Exposed limestone column drums",
      "Lintel fragments with plain moulding",
      "Sand-buried lower courses (extent unknown)",
    ],
    timeline: [
      { year: "1st c. BCE", event: "Probable construction phase (provisional)." },
      { year: "2022", event: "Exposure reported after a sandstorm season." },
      { year: "2025", event: "Submitted to Kenzory; under review." },
    ],
    stories: [
      {
        title: "The guide who kept the coordinates for years",
        author: "Kenzory editorial",
        text: "Demo content. A desert guide recorded the location long before it was reported, fearing looting.",
      },
    ],
    sources: [{ label: "Contributor field notes (unverified)", type: "Community" }],
    contributor: { name: "Nour", level: "Contributor", initials: "N" },
    addedAgo: "12 hours ago",
    saves: 41,
    photos: 9,
  },
  {
    id: "khedivial-palace-tanta",
    name: "Crumbling Khedivial-Era Palace",
    nameAr: "قصر من العصر الخديوي",
    governorate: "Gharbia",
    city: "Tanta",
    category: "Cultural Heritage",
    period: "Khedivial Era",
    approxDate: "c. 1885 CE",
    verification: "unverified",
    distanceKm: 19,
    visitMinutes: 40,
    image: palace,
    gallery: [palace, railway, mosque],
    lat: 30.79,
    lng: 31.0,
    summary:
      "A two-storey arcaded residence of a Delta landowning family, now empty and structurally at risk.",
    description:
      "The facade combines European neoclassical detailing with locally carved capitals, typical of Delta elite housing in the late nineteenth century. Ownership history is contested and no protective listing has been located.",
    whyItMatters:
      "Delta-city domestic architecture from this period is being lost to development faster than it is recorded. Even an unverified record establishes that the building existed and what it looked like.",
    architecture: [
      "Ground-floor arcade with carved capitals",
      "Balustraded first-floor balconies",
      "Shuttered timber windows",
      "Partially collapsed roof parapet",
    ],
    timeline: [
      { year: "c. 1885", event: "Built for a landowning family (attribution unconfirmed)." },
      { year: "1960s", event: "Subdivided into apartments." },
      { year: "2010s", event: "Abandoned." },
    ],
    stories: [
      {
        title: "The neighbours who remember the garden",
        author: "Local resident",
        text: "Demo content. Older neighbours describe a walled garden with a fountain, now built over.",
      },
    ],
    sources: [{ label: "No documentary source located yet", type: "None" }],
    contributor: { name: "Hoda", level: "Contributor", initials: "H" },
    addedAgo: "6 days ago",
    saves: 58,
    photos: 14,
  },
];

export const getPlace = (id: string) => places.find((p) => p.id === id);

export const stories = [
  {
    id: "mosque-village-forgot",
    title: "The Mosque Everyone in the Village Forgot",
    excerpt:
      "For thirty years the door stayed locked. Then a schoolteacher started asking who held the key.",
    author: "Mahmoud",
    readMinutes: 7,
    image: mosque,
    place: "Minya",
  },
  {
    id: "railway-120-years",
    title: "An Abandoned Railway Station With 120 Years of History",
    excerpt:
      "Cane trains, wartime timetables, and a logbook that ends mid-sentence in 1974.",
    author: "Ahmed",
    readMinutes: 9,
    image: railway,
    place: "Sohag",
  },
  {
    id: "ancient-craft-upper-egypt",
    title: "The Story Behind an Ancient Craft in Upper Egypt",
    excerpt:
      "Three workshops remain. Each one weaves a pattern the others no longer recognise.",
    author: "Mariam",
    readMinutes: 6,
    image: nubian,
    place: "Aswan",
  },
];

export const feed = [
  {
    id: "f1",
    kind: "New Discovery",
    title: "An abandoned Ottoman-era structure discovered in Beni Suef",
    body: "Reported near an old canal crossing. Awaiting a second contributor visit before review.",
    author: "Ahmed",
    ago: "2 days ago",
    image: mosque,
    verification: "review" as Verification,
    likes: 128,
    comments: 14,
  },
  {
    id: "f2",
    kind: "Verified",
    title: "Cliff Monastery of Deir al-Qusayr is now Officially Verified",
    body: "Ministry site file matched to the contributor record. Two sources added.",
    author: "Mariam",
    ago: "4 days ago",
    image: coptic,
    verification: "official" as Verification,
    likes: 341,
    comments: 27,
  },
  {
    id: "f3",
    kind: "Photo Set",
    title: "18 new photos added to the Painted Nubian House",
    body: "Interior details and roof construction documented for the first time.",
    author: "Sayed",
    ago: "1 week ago",
    image: nubian,
    verification: "community" as Verification,
    likes: 209,
    comments: 11,
  },
];

export const suggestedSearches = [
  "Hidden places near Luxor",
  "Historic mosques in Minya",
  "Coptic heritage near Cairo",
  "Unknown historical places in Upper Egypt",
];

export const profile = {
  name: "Mahmoud",
  handle: "@mahmoud",
  level: "Heritage Explorer",
  bio: "Documenting provincial Ottoman architecture in Middle Egypt. Weekend field trips, always with a notebook.",
  initials: "M",
  discoveries: 17,
  verified: 11,
  photos: 83,
  saved: 26,
  reputation: 74,
  badges: ["Source-backed submissions", "Field photography", "Minya specialist"],
};
