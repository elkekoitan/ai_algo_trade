'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import translations, { TranslationsType } from './index';

interface TranslationsContextType {
  t: (key: string) => string;
  language: string;
  setLanguage: (lang: string) => void;
  isLoaded: boolean;
}

const TranslationsContext = createContext<TranslationsContextType | undefined>(undefined);

interface TranslationsProviderProps {
  children: ReactNode;
  defaultLanguage?: string;
}

export const TranslationsProvider: React.FC<TranslationsProviderProps> = ({ 
  children, 
  defaultLanguage = 'en' 
}) => {
  const [language, setLanguage] = useState<string>(defaultLanguage);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  useEffect(() => {
    // Get saved language from localStorage or use browser language
    const savedLanguage = localStorage.getItem('language') || 
      (navigator.language.startsWith('tr') ? 'tr' : 'en');
    
    setLanguage(savedLanguage);
    setIsLoaded(true);
  }, []);

  // Function to get translation by key (e.g., "common.loading")
  const t = (key: string): string => {
    const keys = key.split('.');
    let result: any = translations[language as keyof typeof translations];
    
    for (const k of keys) {
      if (result && result[k]) {
        result = result[k];
      } else {
        // Fallback to English if translation is missing
        let fallback: any = translations.en;
        for (const fk of keys) {
          if (fallback && fallback[fk]) {
            fallback = fallback[fk];
          } else {
            return key; // Return the key if translation is missing in both languages
          }
        }
        return typeof fallback === 'string' ? fallback : key;
      }
    }
    
    return typeof result === 'string' ? result : key;
  };

  const handleSetLanguage = (lang: string) => {
    setLanguage(lang);
    localStorage.setItem('language', lang);
  };

  return (
    <TranslationsContext.Provider
      value={{
        t,
        language,
        setLanguage: handleSetLanguage,
        isLoaded
      }}
    >
      {children}
    </TranslationsContext.Provider>
  );
};

export const useTranslations = () => {
  const context = useContext(TranslationsContext);
  
  if (context === undefined) {
    throw new Error('useTranslations must be used within a TranslationsProvider');
  }
  
  return context;
}; 