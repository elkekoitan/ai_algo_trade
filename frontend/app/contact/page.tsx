'use client';

import { motion } from 'framer-motion';
import ContactForm from '@/components/ui/contact-form';
import { useTranslations } from '@/lib/translations/context';

export default function ContactPage() {
  const { t } = useTranslations();
  
  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h1 className="text-3xl font-bold">{t('contact.title')}</h1>
        <p className="text-gray-400">
          ICT Ultra v2: Algo Forge Edition - {t('contact.title')}
        </p>
      </motion.div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <ContactForm />
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gray-900/50 backdrop-blur-lg rounded-xl border border-gray-800 p-6"
        >
          <h2 className="text-xl font-semibold mb-4">ICT Ultra Support</h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-medium text-blue-400">Email</h3>
              <p>support@ictultra.com</p>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-blue-400">Phone</h3>
              <p>+1 (555) 123-4567</p>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-blue-400">Address</h3>
              <p>
                ICT Ultra Headquarters<br />
                123 Trading Street<br />
                Financial District<br />
                New York, NY 10004
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-blue-400">Hours</h3>
              <p>
                Monday - Friday: 9:00 AM - 5:00 PM ET<br />
                Trading Support: 24/7
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
