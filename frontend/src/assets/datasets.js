// Authentic Test Dataset Media & Visual Assets
export const ASSETS = {
  person: "/input/person.jpg",
  tamper: "/input/candidate_same.jpg",
  lookalike: "/input/candidate_different.jpg",
  noface: "/input/no_face.jpg",
  custom: null
};

export const DATASETS = [
  {
    id: "person",
    name: "Tech Executive",
    sub: "input/person.jpg",
    spec: "512×512 • 48.2 KB • YuNet: 0.98",
    hash: "cdbbb4ca45c00dc16ceb08caeb886d0fb24e059ec11880af497ca620d15359a9"
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
    hash: "none"
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
