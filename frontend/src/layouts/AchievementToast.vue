<!-- AchievementToast.vue -->
<template>
    <div class="achievement-toast">
      <div class="achievement-header">
        <div class="achievement-emoji">{{ getEmoji }}</div>
        <div class="achievement-title">{{ title }}</div>
      </div>
      <div class="achievement-score">
        <div class="stars">
          <span 
            v-for="i in 5" 
            :key="i" 
            class="star"
            :class="{ active: i <= score }"
          >★</span>
        </div>
        <div class="score-text">Score: {{ score }}/5</div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'AchievementToast',
    props: {
      title: {
        type: String,
        required: true
      },
      score: {
        type: Number,
        required: true,
        validator: (value) => value >= 0 && value <= 5
      }
    },
    computed: {
      getEmoji() {
        const emojis = {
          0: '😐',
          1: '🙂',
          2: '😊',
          3: '🌟',
          4: '🏆',
          5: '🎉'
        };
        return emojis[this.score] || '🎯';
      }
    }
  }
  </script>
  
  <style>
  /* These styles will help remove the "box in box" appearance by using Vue Toastification's global classes */
  :deep(.Vue-Toastification__toast) {
    padding: 0 !important;
    min-height: auto !important;
    background: none !important;
    box-shadow: none !important;
    max-width: 320px !important;
  }
  
  :deep(.Vue-Toastification__toast-body) {
    padding: 0 !important;
    margin: 0 !important;
  }
  
  .achievement-toast {
    padding: 16px;
    border-radius: 8px;
    background: linear-gradient(145deg, #2a2a72, #009ffd);
    color: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    width: 100%;
  }
  
  .achievement-header {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
  }
  
  .achievement-emoji {
    font-size: 28px;
    margin-right: 12px;
  }
  
  .achievement-title {
    font-weight: bold;
    font-size: 16px;
    flex-grow: 1;
  }
  
  .achievement-score {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .stars {
    display: flex;
  }
  
  .star {
    color: rgba(255, 255, 255, 0.3);
    margin-right: 2px;
    font-size: 18px;
  }
  
  .star.active {
    color: gold;
  }
  
  .score-text {
    font-size: 12px;
    opacity: 0.8;
  }
  </style>