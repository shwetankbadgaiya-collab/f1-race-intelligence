export const TEAM_COLORS: Record<string, string> = {
  'Red Bull': '#3671C6',
  'Red Bull Racing': '#3671C6',
  'red_bull': '#3671C6',
  'Mercedes': '#27F4D2',
  'mercedes': '#27F4D2',
  'Ferrari': '#E8002D',
  'ferrari': '#E8002D',
  'McLaren': '#FF8000',
  'mclaren': '#FF8000',
  'Alpine F1 Team': '#FF87BC',
  'Alpine': '#FF87BC',
  'alpine': '#FF87BC',
  'Renault': '#FFD800',
  'renault': '#FFD800',
  'Aston Martin': '#229971',
  'aston_martin': '#229971',
  'AlphaTauri': '#5E8FAA',
  'alphatauri': '#5E8FAA',
  'Toro Rosso': '#5E8FAA',
  'toro_rosso': '#5E8FAA',
  'RB F1 Team': '#6692FF',
  'rb': '#6692FF',
  'Williams': '#64C4FF',
  'williams': '#64C4FF',
  'Alfa Romeo': '#C92D4B',
  'alfa': '#C92D4B',
  'Sauber': '#52E252',
  'sauber': '#52E252',
  'Haas F1 Team': '#B6BABD',
  'Haas': '#B6BABD',
  'haas': '#B6BABD',
  'Racing Point': '#F596C8',
  'racing_point': '#F596C8',
  'Force India': '#F596C8',
  'force_india': '#F596C8',
  'Lotus F1': '#FFB800',
  'lotus_f1': '#FFB800',
  'Caterham': '#005030',
  'caterham': '#005030',
  'Marussia': '#6E0000',
  'marussia': '#6E0000',
  'Manor Marussia': '#6E0000',
  'manor': '#6E0000',
};

const CHART_PALETTE = [
  '#E10600', '#3671C6', '#27F4D2', '#FF8000', '#FF87BC',
  '#229971', '#5E8FAA', '#64C4FF', '#C92D4B', '#B6BABD',
  '#FFD800', '#F596C8', '#52E252', '#6692FF', '#E8002D',
  '#00D26A', '#FFB800', '#7C3AED', '#F97316', '#06B6D4',
];

export function getTeamColor(teamName: string): string {
  if (TEAM_COLORS[teamName]) return TEAM_COLORS[teamName];
  const lower = teamName.toLowerCase().replace(/\s+/g, '_');
  if (TEAM_COLORS[lower]) return TEAM_COLORS[lower];
  for (const key of Object.keys(TEAM_COLORS)) {
    if (teamName.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(teamName.toLowerCase())) {
      return TEAM_COLORS[key];
    }
  }
  let hash = 0;
  for (let i = 0; i < teamName.length; i++) {
    hash = teamName.charCodeAt(i) + ((hash << 5) - hash);
  }
  return CHART_PALETTE[Math.abs(hash) % CHART_PALETTE.length];
}

export function getChartColor(index: number): string {
  return CHART_PALETTE[index % CHART_PALETTE.length];
}

export { CHART_PALETTE };
