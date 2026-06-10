import { createContext, useContext, useState, ReactNode } from 'react'
import { Locale, Dict, DICT, detectLocale } from './i18n.ts'

type LocaleContextValue = {
  locale: Locale
  t: Dict
  setLocale: (locale: Locale) => void
}

const LocaleContext = createContext<LocaleContextValue>({
  locale: 'de',
  t: DICT.de,
  setLocale: () => {},
})

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>(detectLocale)
  return (
    <LocaleContext.Provider value={{ locale, t: DICT[locale], setLocale }}>
      {children}
    </LocaleContext.Provider>
  )
}

export function useLocale(): LocaleContextValue {
  return useContext(LocaleContext)
}
