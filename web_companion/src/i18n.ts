import deRaw from './locales/de.json'
import enRaw from './locales/en.json'

export type Locale = 'de' | 'en'
export type Dict = { [K in keyof typeof deRaw]: string }

export const DICT: Record<Locale, Dict> = {
  de: deRaw,
  en: enRaw,
}

export function fillIn(template: string, values: Record<string, string>): string {
  return Object.entries(values).reduce(
    (str, [key, val]) => str.replace(`{${key}}`, val),
    template,
  )
}

export function detectLocale(): Locale {
  if (typeof navigator === 'undefined') return 'de'
  return navigator.language.startsWith('en') ? 'en' : 'de'
}
