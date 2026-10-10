<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from 'vue';
import logoUrl from './assets/edigit-logo.svg';
import { privacyAreas } from './data/privacyAreas';

const screen = ref('home');
const selectedArea = ref(null);
const selectedQuestion = ref(null);
const showQuestionDetails = ref(false);
const lead = ref({ firstName: '', lastName: '', email: '', badge: '' });
const savedLeads = ref(loadLeads());
const cameraActive = ref(false);
const cameraError = ref('');
const videoEl = ref(null);
let mediaStream = null;
let scanTimer = null;

const selectedAreaStyle = computed(() => {
  if (!selectedArea.value) return {};
  return {
    '--area-color': selectedArea.value.color,
    '--area-accent': selectedArea.value.accent
  };
});

function goHome() {
  stopCamera();
  screen.value = 'home';
  selectedArea.value = null;
  selectedQuestion.value = null;
  showQuestionDetails.value = false;
}

function startGame() {
  stopCamera();
  showQuestionDetails.value = false;
  screen.value = 'game';
}

function chooseArea(area) {
  selectedArea.value = area;
  selectedQuestion.value = randomItem(area.questions);
  showQuestionDetails.value = false;
  screen.value = 'question';
}

function randomItem(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function towerFell() {
  selectedArea.value = null;
  selectedQuestion.value = null;
  showQuestionDetails.value = false;
  screen.value = 'fallen';
}

function revealQuestionDetails() {
  showQuestionDetails.value = true;
}

function saveLead() {
  const nextLead = {
    firstName: lead.value.firstName.trim(),
    lastName: lead.value.lastName.trim(),
    email: lead.value.email.trim(),
    badge: lead.value.badge.trim(),
    createdAt: new Date().toISOString()
  };

  if (!nextLead.firstName && !nextLead.lastName && !nextLead.email && !nextLead.badge) {
    return;
  }

  savedLeads.value = [nextLead, ...savedLeads.value];
  localStorage.setItem('privacy-tower-leads', JSON.stringify(savedLeads.value));
  lead.value = { firstName: '', lastName: '', email: '', badge: '' };
}

function loadLeads() {
  try {
    return JSON.parse(localStorage.getItem('privacy-tower-leads') || '[]');
  } catch {
    return [];
  }
}

function exportCsv() {
  const header = ['Nome', 'Cognome', 'Email', 'Badge', 'Data'];
  const rows = savedLeads.value.map((item) => [
    item.firstName,
    item.lastName,
    item.email,
    item.badge,
    item.createdAt
  ]);
  const csv = [header, ...rows].map((row) => row.map(csvCell).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'contatti-privacy-tower.csv';
  link.click();
  URL.revokeObjectURL(url);
}

function csvCell(value) {
  return `"${String(value || '').replaceAll('"', '""')}"`;
}

async function startCamera() {
  cameraError.value = '';

  if (!navigator.mediaDevices?.getUserMedia) {
    cameraError.value = 'Camera non disponibile su questo browser.';
    return;
  }

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' },
      audio: false
    });
    cameraActive.value = true;
    await nextTick();
    videoEl.value.srcObject = mediaStream;
    await videoEl.value.play();
    startBadgeScan();
  } catch {
    cameraError.value = 'Non riesco ad aprire la camera. Puoi inserire i dati a mano.';
  }
}

function startBadgeScan() {
  if (!('BarcodeDetector' in window)) {
    cameraError.value = 'Scanner automatico non supportato qui: usa la camera come riferimento e compila il form.';
    return;
  }

  const detector = new window.BarcodeDetector({
    formats: ['qr_code', 'code_128', 'code_39', 'ean_13', 'pdf417']
  });

  scanTimer = window.setInterval(async () => {
    if (!videoEl.value) return;
    try {
      const codes = await detector.detect(videoEl.value);
      if (codes.length > 0) {
        lead.value.badge = codes[0].rawValue;
        stopCamera();
      }
    } catch {
      cameraError.value = 'Lettura automatica non riuscita. Inserisci i dati manualmente.';
      stopCamera();
    }
  }, 900);
}

function stopCamera() {
  if (scanTimer) {
    window.clearInterval(scanTimer);
    scanTimer = null;
  }
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
  cameraActive.value = false;
}

onBeforeUnmount(stopCamera);
</script>

<template>
  <main class="app-shell" :style="selectedAreaStyle">
    <button v-if="screen !== 'home'" class="home-button" type="button" @click="goHome">
      Inizio
    </button>

    <section v-if="screen === 'home'" class="screen home-screen">
      <div class="brand-lockup">
        <img class="brand-logo" :src="logoUrl" alt="E-Digit" />
        <div>
          <strong>E-Digit</strong>
          <span>Digital Compliance per le PMI: semplice, sicura, accessibile.</span>
        </div>
      </div>
      <div class="home-copy">
        <h1>Sei sicuro che ogni tassello della tua data privacy sia al posto giusto?</h1>
        <p>
          Estrai un tassello dalla torre, scegli il colore sullo schermo e scopri quale area della compliance mettiamo alla prova insieme a E-Digit.
        </p>
      </div>
      <button class="primary-cta" type="button" @click="startGame">
        Iniziamo
      </button>
    </section>

    <section v-else-if="screen === 'game'" class="screen game-screen">
      <header class="game-header">
        <div class="small-brand">
          <img class="small-logo" :src="logoUrl" alt="E-Digit" />
          <strong>E-Digit</strong>
        </div>
        <div>
          <h2>Scegli il colore del tassello che hai estratto</h2>
        </div>
      </header>

      <div class="area-grid">
        <template v-for="(area, index) in privacyAreas" :key="area.id">
          <button
            class="area-tile"
            :style="{
              '--tile-color': area.color,
              '--tile-accent': area.accent,
              '--tile-ink': area.ink,
              '--tile-border': area.border,
              '--tile-bg': area.background,
              '--tile-hover-bg': area.hoverBackground
            }"
            type="button"
            @click="chooseArea(area)"
          >
            <div>
              <p class="area-short">{{ area.shortName }}</p>
              <h3>{{ area.name }}</h3>
              <p>{{ area.subtitle }}</p>
            </div>
          </button>
          <button v-if="index === 2" class="fallen-button" type="button" @click="towerFell">
            La torre è caduta
          </button>
        </template>
      </div>
    </section>

    <section v-else-if="screen === 'question'" class="screen question-screen">
      <div
        class="question-band"
        role="button"
        tabindex="0"
        @click="revealQuestionDetails"
        @keydown.enter.prevent="revealQuestionDetails"
        @keydown.space.prevent="revealQuestionDetails"
      >
        <p class="eyebrow">{{ selectedArea.name }}</p>
        <h2>{{ selectedQuestion.domanda }}</h2>
        <div v-if="showQuestionDetails" class="question-notes">
          <p class="question-answer">{{ selectedQuestion.risposta }}</p>
          <p class="question-context">{{ selectedQuestion.gancio_sales }}</p>
        </div>
      </div>
    </section>

    <section v-else class="screen fallen-screen">
      <div class="fallen-copy">
        <div class="small-brand">
          <img class="small-logo" :src="logoUrl" alt="E-Digit" />
          <strong>E-Digit</strong>
        </div>
        <p class="eyebrow">Niente panico</p>
        <h2>Quando la torre traballa, EDigit puo aiutarti a rimettere ordine.</h2>
        <p>
          Lasciaci un contatto e ti mostriamo come conduciamo audit privacy con E-Digit e MisterCompliance: evidenze, responsabilita e azioni tracciate in modo semplice.
        </p>
      </div>

      <form class="lead-form" @submit.prevent="saveLead">
        <label>
          Nome
          <input v-model="lead.firstName" autocomplete="given-name" />
        </label>
        <label>
          Cognome
          <input v-model="lead.lastName" autocomplete="family-name" />
        </label>
        <label>
          Email
          <input v-model="lead.email" type="email" autocomplete="email" />
        </label>
        <label>
          Badge o note
          <input v-model="lead.badge" autocomplete="off" />
        </label>

        <div class="camera-panel">
          <video v-show="cameraActive" ref="videoEl" muted playsinline></video>
          <p v-if="cameraError">{{ cameraError }}</p>
          <button v-if="!cameraActive" type="button" class="secondary-button" @click="startCamera">
            Scannerizza badge
          </button>
          <button v-else type="button" class="secondary-button" @click="stopCamera">
            Chiudi camera
          </button>
        </div>

        <button class="primary-cta compact" type="submit">
          Salva contatto
        </button>
      </form>

      <div class="lead-tools">
        <span>{{ savedLeads.length }} contatti salvati su questo iPad</span>
        <button type="button" :disabled="savedLeads.length === 0" @click="exportCsv">
          Esporta CSV
        </button>
      </div>
    </section>
  </main>
</template>
