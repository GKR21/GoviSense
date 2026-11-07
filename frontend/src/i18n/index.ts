import { en } from "./en"
import { si } from "./si"
import { ta } from "./ta"
import type { Language } from "../types/farmer"

export const translations = {
  en,
  si,
  ta,
} as const

export type TranslationKey = keyof typeof en

export function getTranslations(lang: Language) {
  return translations[lang] || translations.en
}

