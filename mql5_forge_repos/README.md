# MQL5 Algo Forge Git Entegrasyonu

Bu klasör, MetaTrader 5 platformunun yeni sürümü (5100+) ile gelen MQL5 Algo Forge ve Git entegrasyonu özelliklerini kullanmak için tasarlanmıştır.

## MQL5 Algo Forge Nedir?

MQL5 Algo Forge, MetaQuotes tarafından MetaTrader 5 platformunun 5100 sürümüyle birlikte sunulan, geliştiriciler için tam teşekküllü bir sosyal ağ ve proje yönetim platformudur. Subversion yerine Git kullanarak, kod yönetiminde daha fazla güvenilirlik ve esneklik sağlar.

## Klasör Yapısı

```
mql5_forge_repos/
├── strategies/       # Trading stratejileri
├── indicators/       # Teknik göstergeler
└── libraries/        # Yeniden kullanılabilir MQL5 kütüphaneleri
```

## Git Entegrasyonunun Avantajları

1. **Esnek Dallandırma ve Birleştirme**: Yeni özellikler veya deneyler için ayrı dallar oluşturun ve ardından bunları ana proje sürümüyle kolayca birleştirin.
2. **Daha Hızlı Depo İşlemleri**: Git, tüm verileri yerel olarak depolar, bu da işlemleri (commit, dallar arası geçiş, değişiklikleri karşılaştırma) önemli ölçüde hızlandırır.
3. **Çevrimdışı Çalışma**: Sürekli bir sunucu bağlantısına gerek olmadan değişiklikleri yerel olarak işleyebilir ve uygun olduğunda çevrimiçi depoya gönderebilirsiniz.
4. **Gelişmiş Değişiklik Takibi**: Sürüm geçmişini kolayca inceleyebilir, zaman damgaları ve yazarlarla değişiklikleri takip edebilir ve önceki sürümlere sorunsuz bir şekilde geri dönebilirsiniz.

## ICT Ultra v2 ile Entegrasyon

ICT Ultra v2 platformu, MQL5 Algo Forge ile tam entegrasyon sağlar:

1. **Repo Listeleme**: Platformdan doğrudan MQL5 Algo Forge'daki Git repolarınızı görüntüleyebilirsiniz.
2. **Klonlama ve Senkronizasyon**: Seçtiğiniz repoları bu klasöre klonlayabilir ve senkronize edebilirsiniz.
3. **Commit ve Push**: Platform arayüzünden doğrudan değişikliklerinizi commit edebilir ve Algo Forge'a push edebilirsiniz.
4. **MT5 Entegrasyonu**: Bu klasördeki dosyalar ile MT5'in `MQL5/Experts` veya `MQL5/Indicators` klasörleri arasında otomatik senkronizasyon sağlanır.

## Başlarken

### 1. MetaTrader 5 Sürüm 5100+ Kurulumu

MetaTrader 5 platformunun en az 5100 sürümünü kurduğunuzdan emin olun. Bu sürüm, Git entegrasyonu ve MQL5 Algo Forge özelliklerini içerir.

### 2. MQL5 Algo Forge Hesabı

1. MQL5.community hesabınız ile giriş yapın.
2. MQL5 Algo Forge'a erişim için hesabınızı doğrulayın.

### 3. ICT Ultra v2 ile Repo Yönetimi

1. ICT Ultra v2 platformunun "Forge" sekmesine gidin.
2. "Repolarım" bölümünden mevcut repolarınızı görüntüleyin.
3. "Repo Klonla" butonu ile seçtiğiniz repoyu bu klasöre klonlayın.
4. Değişikliklerinizi yapın ve platform üzerinden commit/push işlemlerini gerçekleştirin.

## Örnek İş Akışı

1. ICT Ultra v2 üzerinden bir ICT Order Block stratejisi reposu oluşturun.
2. Repoyu bu klasöre klonlayın.
3. Stratejiyi geliştirin ve test edin.
4. Değişikliklerinizi commit edin ve Algo Forge'a push edin.
5. MT5 platformunda stratejiyi doğrudan kullanın.

## Önemli Notlar

- Bu klasördeki tüm değişiklikler, Git versiyon kontrolü altındadır.
- Değişikliklerinizi düzenli olarak commit edin ve uzak repoya push edin.
- Ekip çalışması için branch'ler oluşturun ve merge request'ler kullanın.
- MT5 platformunda yapılan değişikliklerin bu klasöre senkronize edilmesi için platform ayarlarını kontrol edin. 