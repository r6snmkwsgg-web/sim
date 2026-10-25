// International and pro-path draft prospects. They never play college ball;
// they fill the NBA Draft slots that real drafts give to players from abroad.

export interface IntlPool {
  country: string;
  clubs: string[];
  first: string[];
  last: string[];
  weight: number;
}

export const INTL: IntlPool[] = [
  { country: "France", weight: 5, clubs: ["ASVEL", "Paris Basketball", "AS Monaco", "Cholet", "JL Bourg", "Nanterre 92"], first: ["Noah", "Joan", "Nolan", "Mathis", "Ilan", "Rayan", "Hugo", "Moussa", "Bilal", "Enzo"], last: ["Traoré", "Beringer", "Diallo", "Cissé", "Fofana", "Lefèvre", "Mbaye", "Rupert", "Coulibaly", "Morel"] },
  { country: "Spain", weight: 2, clubs: ["Real Madrid", "FC Barcelona", "Joventut", "Valencia Basket", "Unicaja"], first: ["Pablo", "Hugo", "Izan", "Mario", "Sergio", "Álvaro"], last: ["García", "Fernández", "Saint-Supéry", "Almansa", "Ruiz", "Torres"] },
  { country: "Serbia", weight: 2, clubs: ["Mega Basket", "Partizan", "Crvena Zvezda", "FMP"], first: ["Nikola", "Stefan", "Marko", "Vuk", "Luka", "Bogdan"], last: ["Jović", "Petrović", "Marković", "Topić", "Nikolić", "Ilić"] },
  { country: "Australia", weight: 3, clubs: ["NBL Next Stars", "Sydney Kings", "Melbourne United", "Perth Wildcats"], first: ["Josh", "Rocco", "Alex", "Lachlan", "Will", "Tyrese"], last: ["Green", "Zikarsky", "Toohey", "Proctor", "Mitchell", "Harris"] },
  { country: "Germany", weight: 2, clubs: ["ratiopharm Ulm", "Bayern Munich", "ALBA Berlin", "Bonn"], first: ["Ben", "Luka", "Jonas", "Noah", "Tim", "Ariel"], last: ["Saibou", "Wagner", "Fischer", "Hukporti", "Krämer", "Schröder"] },
  { country: "Lithuania", weight: 1, clubs: ["Žalgiris", "Rytas"], first: ["Kasparas", "Matas", "Ignas", "Rokas"], last: ["Jakučionis", "Buzelis", "Sargiūnas", "Grigonis"] },
  { country: "Turkey", weight: 1, clubs: ["Fenerbahçe", "Anadolu Efes", "Galatasaray"], first: ["Alperen", "Kerem", "Emir", "Arda"], last: ["Yılmaz", "Öztürk", "Kaya", "Demir"] },
  { country: "Greece", weight: 1, clubs: ["Panathinaikos", "Olympiacos", "AEK Athens"], first: ["Nikos", "Giannis", "Kostas", "Thanos"], last: ["Papadopoulos", "Rogkavopoulos", "Mitoglou", "Kalaitzakis"] },
  { country: "Italy", weight: 1, clubs: ["Olimpia Milano", "Virtus Bologna"], first: ["Matteo", "Gabriele", "Lorenzo", "Luca"], last: ["Procida", "Spagnolo", "Rossi", "Bianchi"] },
  { country: "Slovenia", weight: 1, clubs: ["Cedevita Olimpija", "Krka"], first: ["Jaka", "Žiga", "Luka", "Matic"], last: ["Blažič", "Novak", "Kranjc", "Horvat"] },
  { country: "Israel", weight: 1, clubs: ["Maccabi Tel Aviv", "Hapoel Tel Aviv"], first: ["Ben", "Yam", "Deni", "Roman"], last: ["Saraf", "Madar", "Cohen", "Levi"] },
  { country: "Canada", weight: 1, clubs: ["NBA Academy Latin America", "Orangeville Prep"], first: ["Jaden", "Olivier", "Leonard", "Shai"], last: ["Rousseau", "Tremblay", "Gagnon", "Bennett"] },
  { country: "Nigeria", weight: 1, clubs: ["NBA Academy Africa"], first: ["Chukwuma", "Ifeanyi", "Tobi", "Emeka"], last: ["Okafor", "Adebayo", "Eze", "Nwosu"] },
  { country: "Japan", weight: 1, clubs: ["B.League Alvark Tokyo", "Chiba Jets"], first: ["Yuki", "Rui", "Kai", "Sota"], last: ["Kawamura", "Tominaga", "Watanabe", "Hachimura"] },
  { country: "USA", weight: 3, clubs: ["Overtime Elite", "G League Ignite"], first: ["Amen", "Ausar", "Jaylen", "Tyler", "Matas", "Kiyan"], last: ["Thompson", "Bates", "Anderson", "Wright", "Henderson", "Moore"] },
];
