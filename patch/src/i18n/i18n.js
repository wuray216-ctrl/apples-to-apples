import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './locales/en.json'
import zh from './locales/zh.json'
import es from './locales/es.json'

function getDefaultLang() {
  const saved = localStorage.getItem('apples-lang')
  if (saved && ['en', 'zh', 'es'].includes(saved)) return saved
  const browserLang = navigator.language?.slice(0, 2)
  if (['zh', 'es'].includes(browserLang)) return browserLang
  return 'en'
}

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, zh: { translation: zh }, es: { translation: es } },
  lng: getDefaultLang(),
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
