'use client';

import { useState } from 'react';
import { Button } from './button';
import { useTranslations } from '@/lib/translations/context';

const ContactForm = () => {
  const { t } = useTranslations();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Here you would normally send the data to your backend
      // For now, we'll just simulate a successful submission
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSubmitStatus('success');
      setFormData({
        name: '',
        email: '',
        message: ''
      });
    } catch (error) {
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur-lg rounded-xl border border-gray-800 p-6">
      <h2 className="text-xl font-semibold mb-4">{t('contact.title')}</h2>
      
      {submitStatus === 'success' ? (
        <div className="bg-green-900/20 border border-green-800/50 rounded-lg p-4 text-green-400">
          <p>{t('contact.success')}</p>
        </div>
      ) : submitStatus === 'error' ? (
        <div className="bg-red-900/20 border border-red-800/50 rounded-lg p-4 text-red-400">
          <p>{t('contact.error')}</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-400 mb-1">
              {t('contact.name')}
            </label>
            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
            />
          </div>
          
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-400 mb-1">
              {t('contact.email')}
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
            />
          </div>
          
          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-400 mb-1">
              {t('contact.message')}
            </label>
            <textarea
              id="message"
              name="message"
              rows={4}
              value={formData.message}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
            />
          </div>
          
          <Button
            type="submit"
            disabled={isSubmitting}
            className="w-full"
          >
            {isSubmitting ? t('common.loading') : t('contact.send')}
          </Button>
        </form>
      )}
    </div>
  );
};

export default ContactForm;
