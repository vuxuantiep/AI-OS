import { MetadataRoute } from 'next'
 
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'TRACE AI OS CEO Dashboard',
    short_name: 'TRACE AI',
    description: 'Zentrales Interface für die Steuerung der Backend-Agenten.',
    start_url: '/',
    display: 'standalone',
    background_color: '#030712',
    theme_color: '#030712',
    icons: [
      {
        src: 'https://picsum.photos/192/192',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: 'https://picsum.photos/512/512',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  }
}
