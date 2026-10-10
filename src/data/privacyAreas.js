import questionBank from '../../domande_privacy_sanita.json';

const areaStyles = {
  GIALLO: {
    shortName: 'Diritti',
    subtitle: 'Consensi, informative e richieste dei pazienti gestite senza improvvisare',
    color: '#f2b705',
    accent: '#fff4c9'
  },
  FUCSIA: {
    shortName: 'Personale',
    subtitle: 'Ruoli, accessi ai sistemi e formazione davvero tracciabile',
    color: '#d9368a',
    accent: '#ffe0f0'
  },
  VERDE: {
    shortName: 'Fornitori',
    subtitle: 'Responsabili esterni, contratti, subfornitori e verifiche periodiche',
    color: '#10a16b',
    accent: '#dcf8ec'
  },
  'ROSSO PORPORA': {
    shortName: 'Sicurezza',
    subtitle: 'Misure tecniche, log, backup e protezione concreta dei dati',
    color: '#8d1f3d',
    accent: '#ffe0e8'
  },
  BLU: {
    shortName: 'Segnalazioni',
    subtitle: 'Canali di segnalazione, riservatezza e gestione delle evidenze',
    color: '#0f74bd',
    accent: '#d7efff'
  },
  'BIANCO E NERO': {
    shortName: 'Data breach',
    subtitle: 'Incidenti, notifiche, tempi di risposta e responsabilità operative',
    color: '#d9dee7',
    accent: '#101820',
    ink: '#101820',
    border: '#ffffff',
    background: '#e1e4ea',
    hoverBackground: '#d6dbe3'
  },
  VERDE_LEGACY: {
    shortName: 'Diritti',
    subtitle: 'Consenso, trasparenza e diritti dei pazienti',
    color: '#10a16b',
    accent: '#dcf8ec'
  },
  BLU_LEGACY: {
    shortName: 'Personale',
    subtitle: 'Autorizzazioni, accessi e formazione',
    color: '#0f74bd',
    accent: '#d7efff'
  },
  GIALLO_LEGACY: {
    shortName: 'Fornitori',
    subtitle: 'Responsabili esterni, contratti e subfornitori',
    color: '#f2b705',
    accent: '#fff4c9'
  },
  ARANCIONE: {
    shortName: 'Sicurezza',
    subtitle: 'Misure tecniche, sistemi e protezione dati',
    color: '#ed6a2c',
    accent: '#ffe5d7'
  },
  VIOLA: {
    shortName: 'Segnalazioni',
    subtitle: 'Whistleblowing, canali e riservatezza',
    color: '#7d4cc2',
    accent: '#eadfff'
  },
  ROSSO: {
    shortName: 'Data breach',
    subtitle: 'Incidenti, notifiche e gestione emergenze',
    color: '#d9365f',
    accent: '#ffe0e8'
  }
};

export const privacyAreas = questionBank.aree.map((area) => {
  const colorCode = String(area.codice_colore || '').trim().toUpperCase();
  const style = areaStyles[colorCode] || {
    shortName: area.area,
    subtitle: 'Privacy, compliance e processi sanitari',
    color: '#3b4d82',
    accent: '#d7dee8'
  };

  return {
  id: colorCode.toLowerCase(),
  name: area.area,
  shortName: style.shortName,
  subtitle: style.subtitle,
  colorCode,
  color: style.color,
  accent: style.accent,
  ink: style.ink || style.color,
  border: style.border || style.color,
  background: style.background,
  hoverBackground: style.hoverBackground,
  questions: area.domande
  };
});
