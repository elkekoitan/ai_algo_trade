'use client';

import { useState, useEffect } from 'react';
import { Globe } from 'lucide-react';
import { Button } from './button';

interface LanguageSwitcherProps {
  onLanguageChange?: (lang: string) => void;
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ onLanguageChange }) => {
  const [language, setLanguage] = useState<string>('en');
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'tr', name: 'Türkçe' }
  ];

  useEffect(() => {
    // Get saved language from localStorage or use browser language
    const savedLanguage = localStorage.getItem('language') || 
      (navigator.language.startsWith('tr') ? 'tr' : 'en');
    
    setLanguage(savedLanguage);
  }, []);

  const handleLanguageChange = (lang: string) => {
    setLanguage(lang);
    localStorage.setItem('language', lang);
    setIsOpen(false);
    
    if (onLanguageChange) {
      onLanguageChange(lang);
    }
  };

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        className="flex items-center gap-1 text-gray-400 hover:text-white"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Globe className="h-4 w-4" />
        <span className="text-xs uppercase">{language}</span>
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-1 w-32 rounded-md bg-gray-900 border border-gray-800 shadow-lg z-50">
          <div className="py-1">
            {languages.map((lang) => (
              <button
                key={lang.code}
                className={`block w-full text-left px-4 py-2 text-sm ${
                  language === lang.code
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800'
                }`}
                onClick={() => handleLanguageChange(lang.code)}
              >
                {lang.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LanguageSwitcher; 