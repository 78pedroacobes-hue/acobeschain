def estimar_regalias(vistas_youtube=0, streams_audio=0, vistas_facebook=0):
    # Tasas promedio referenciales de la industria (en USD por cada 1,000 reproducciones)
    # Varían según el país de la audiencia, tipo de suscripción y acuerdos de distribución.
    rpm_youtube_min, rpm_youtube_max = 0.80, 3.00      # YouTube (AdSense / Content ID)
    rpm_streaming_min, rpm_streaming_max = 2.50, 4.50  # Apple Music / Spotify / Streaming
    rpm_facebook_min, rpm_facebook_max = 0.15, 0.80    # Facebook / Reels (Rights Manager)

    yt_min = (vistas_youtube / 1000) * rpm_youtube_min
    yt_max = (vistas_youtube / 1000) * rpm_youtube_max

    st_min = (streams_audio / 1000) * rpm_streaming_min
    st_max = (streams_audio / 1000) * rpm_streaming_max

    fb_min = (vistas_facebook / 1000) * rpm_facebook_min
    fb_max = (vistas_facebook / 1000) * rpm_facebook_max

    total_min = yt_min + st_min + fb_min
    total_max = yt_max + st_max + fb_max

    print("=== PROYECCIÓN REFERENCIAL DE REGALÍAS (USD) ===")
    print(f"YouTube ({vistas_youtube:,} vistas): ${yt_min:,.2f} - ${yt_max:,.2f}")
    print(f"Streaming Audio ({streams_audio:,} streams): ${st_min:,.2f} - ${st_max:,.2f}")
    print(f"Facebook ({vistas_facebook:,} vistas): ${fb_min:,.2f} - ${fb_max:,.2f}")
    print("-" * 48)
    print(f"Rango Total Estimado: ${total_min:,.2f} - ${total_max:,.2f} USD\n")

if __name__ == "__main__":
    # Ejemplo de prueba: sustituye estos números por las cifras que ves en tus canales
    estimar_regalias(
        vistas_youtube=50000,
        streams_audio=15000,
        vistas_facebook=30000
    )
