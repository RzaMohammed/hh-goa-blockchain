// Authentic Test Dataset Vector SVGs (Clean Passport / Dataset Photo Aesthetics)
export const ASSETS = {
  person: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 200 200'%3E%3Crect width='200' height='200' fill='%23132019'/%3E%3Cdefs%3E%3ClinearGradient id='skin' x1='0' y1='0' x2='0' y2='1'%3E%3Cstop offset='0%25' stop-color='%23fed7aa'/%3E%3Cstop offset='100%25' stop-color='%23fdba74'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx='100' cy='85' r='42' fill='url(%23skin)'/%3E%3Cpath d='M65 72 Q100 48 135 72 Q120 44 100 44 Q80 44 65 72' fill='%231c1917'/%3E%3Ccircle cx='85' cy='82' r='3.5' fill='%230f172a'/%3E%3Ccircle cx='115' cy='82' r='3.5' fill='%230f172a'/%3E%3Cpath d='M98 88 L102 96 L96 98' fill='none' stroke='%23ea580c' stroke-width='2' stroke-linecap='round'/%3E%3Cpath d='M88 108 Q100 116 112 108' fill='none' stroke='%23b91c1c' stroke-width='2.5' stroke-linecap='round'/%3E%3Crect x='74' y='76' width='20' height='13' rx='2' fill='none' stroke='%230369a1' stroke-width='2'/%3E%3Crect x='106' y='76' width='20' height='13' rx='2' fill='none' stroke='%230369a1' stroke-width='2'/%3E%3Cline x1='94' y1='82' x2='106' y2='82' stroke='%230369a1' stroke-width='2'/%3E%3Cpath d='M40 180 Q100 132 160 180 Z' fill='%231e3a5f'/%3E%3Cpolygon points='100,140 94,180 106,180' fill='%23facc15'/%3E%3C/svg%3E",
  tamper: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 200 200'%3E%3Crect width='200' height='200' fill='%23132019'/%3E%3Cdefs%3E%3ClinearGradient id='skinT' x1='0' y1='0' x2='0' y2='1'%3E%3Cstop offset='0%25' stop-color='%23fed7aa'/%3E%3Cstop offset='100%25' stop-color='%23fdba74'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx='100' cy='85' r='42' fill='url(%23skinT)'/%3E%3Cpath d='M65 72 Q100 48 135 72 Q120 44 100 44 Q80 44 65 72' fill='%231c1917'/%3E%3Ccircle cx='85' cy='82' r='3.5' fill='%230f172a'/%3E%3Ccircle cx='115' cy='82' r='3.5' fill='%230f172a'/%3E%3Cpath d='M98 88 L102 96 L96 98' fill='none' stroke='%23ea580c' stroke-width='2' stroke-linecap='round'/%3E%3Cpath d='M88 108 Q100 116 112 108' fill='none' stroke='%23b91c1c' stroke-width='2.5' stroke-linecap='round'/%3E%3Crect x='74' y='76' width='20' height='13' rx='2' fill='none' stroke='%230369a1' stroke-width='2'/%3E%3Crect x='106' y='76' width='20' height='13' rx='2' fill='none' stroke='%230369a1' stroke-width='2'/%3E%3Cline x1='94' y1='82' x2='106' y2='82' stroke='%230369a1' stroke-width='2'/%3E%3Cpath d='M40 180 Q100 132 160 180 Z' fill='%231e3a5f'/%3E%3Cpolygon points='100,140 94,180 106,180' fill='%23facc15'/%3E%3Crect x='30' y='30' width='140' height='140' fill='none' stroke='%23ef4444' stroke-dasharray='4 4' stroke-width='1.5'/%3E%3C/svg%3E",
  lookalike: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 200 200'%3E%3Crect width='200' height='200' fill='%23132019'/%3E%3Cdefs%3E%3ClinearGradient id='skinL' x1='0' y1='0' x2='0' y2='1'%3E%3Cstop offset='0%25' stop-color='%23fde047'/%3E%3Cstop offset='100%25' stop-color='%23eab308'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx='100' cy='85' r='42' fill='url(%23skinL)'/%3E%3Cpath d='M65 70 Q100 45 135 70 Q120 40 100 40 Q80 40 65 70' fill='%23292524'/%3E%3Ccircle cx='86' cy='82' r='3.5' fill='%230f172a'/%3E%3Ccircle cx='114' cy='82' r='3.5' fill='%230f172a'/%3E%3Cpath d='M75 100 Q100 135 125 100 Q100 120 75 100' fill='%23292524'/%3E%3Cpath d='M40 180 Q100 130 160 180 Z' fill='%23334155'/%3E%3C/svg%3E",
  noface: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 200 200'%3E%3Crect width='200' height='200' fill='%23062316'/%3E%3Cpolygon points='0,140 50,85 100,140 150,75 200,150 200,200 0,200' fill='%2314532d'/%3E%3Ccircle cx='150' cy='48' r='18' fill='%23fef08a' opacity='0.9'/%3E%3Cpath d='M0 160 Q60 130 120 165 T200 160 L200 200 L0 200 Z' fill='%23052e16'/%3E%3C/svg%3E"
};

export const DATASETS = [
  {
    id: "person",
    name: "Tech Executive",
    sub: "input/person.jpg",
    spec: "512×512 • 48.2 KB • YuNet: 0.98",
    hash: "a7f28c11e3895a98d0f1982b6c934b071295b9c7fa689255627a9446d1e43e2f"
  },
  {
    id: "tamper",
    name: "Tamper Attack Case",
    sub: "input/candidate_same.jpg",
    spec: "1-Byte Mod • CRC Fail",
    hash: "b893c12988cb62804c86125026b91129b860269389f417a80b8e291244e3b1c9"
  },
  {
    id: "lookalike",
    name: "Lookalike Subject",
    sub: "input/candidate_different.jpg",
    spec: "512×512 • Cosine: 0.68",
    hash: "5a41df90e3895a98d0f1982b6c934b071295b9c7fa689255627a9446d1e43e2f"
  },
  {
    id: "noface",
    name: "Landscape (No Face)",
    sub: "input/no_face.jpg",
    spec: "Nature Scene • 0 Faces",
    hash: "a7f28c11e3895a98d0f1982b6c934b071295b9c7fa689255627a9446d1e43e2f"
  }
];

export const SCENARIOS = [
  {
    id: "verified",
    label: "Verified",
    score: "94.8% Match",
    status: "verified",
    note: "Authentic face match recorded & notarized on-chain.",
    datasetId: "person"
  },
  {
    id: "tampered",
    label: "Tampered",
    score: "Audit X",
    status: "tampered",
    note: "Altered file bytes fail SHA-256 cryptographic check.",
    datasetId: "tamper"
  },
  {
    id: "lowmatch",
    label: "Low Match",
    score: "68.2%",
    status: "lowmatch",
    note: "Distant lookalike fails the 85.0% threshold gate.",
    datasetId: "lookalike"
  },
  {
    id: "noface",
    label: "No Face",
    score: "0 Detected",
    status: "noface",
    note: "Image lacks human face; halts at Stage 1.",
    datasetId: "noface"
  }
];
