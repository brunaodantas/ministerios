import asyncio
import os
from pathlib import Path
from urllib.parse import quote
from PIL import Image

BASE  = Path(__file__).parent
HTML  = BASE / "slides.html"
PNGS  = BASE / "slides_png"
PDF   = BASE / "RELATORIO-MINSAUDE-MAIO2026.pdf"

async def run():
    from playwright.async_api import async_playwright

    PNGS.mkdir(exist_ok=True)

    url = "file://" + quote(str(HTML))

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,   # 2x -> 3840x2160 para maxima nitidez
        )

        await page.goto(url)
        await page.wait_for_timeout(3000)   # aguarda fontes e imagens

        slides = await page.query_selector_all(".slide")
        print(f"Encontrados {len(slides)} slides")

        png_files = []
        for i, slide in enumerate(slides):
            out = PNGS / f"slide_{i+1:02d}.png"
            await slide.screenshot(path=str(out), type="png")
            png_files.append(out)
            print(f"  slide {i+1:02d}.png")

        await browser.close()

    print("\nGerando PDF...")
    images = [Image.open(f).convert("RGB") for f in sorted(png_files)]
    images[0].save(
        str(PDF),
        save_all=True,
        append_images=images[1:],
        resolution=144,
    )

    size_mb = PDF.stat().st_size / 1_048_576
    print(f"\nPDF gerado: {PDF}")
    print(f"Paginas: {len(images)}")
    print(f"Tamanho: {size_mb:.1f} MB")

asyncio.run(run())
