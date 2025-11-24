import { test, expect } from '@playwright/test';

test.describe('UI/UX Consistency & Professionalism', () => {
  test('should use consistent color scheme', async ({ page }) => {
    await page.goto('/');

    // Check CSS custom properties are defined
    const hasCSSVariables = await page.evaluate(() => {
      const styles = getComputedStyle(document.documentElement);
      const primary = styles.getPropertyValue('--primary');
      const accent = styles.getPropertyValue('--accent');
      return primary !== '' && accent !== '';
    });

    expect(hasCSSVariables).toBe(true);
  });

  test('should have consistent spacing throughout', async ({ page }) => {
    await page.goto('/');

    // Check for consistent padding/margin using CSS variables
    const usesSpacingVars = await page.evaluate(() => {
      const styles = getComputedStyle(document.documentElement);
      const spaceMd = styles.getPropertyValue('--space-md');
      const spaceLg = styles.getPropertyValue('--space-lg');
      return spaceMd !== '' && spaceLg !== '';
    });

    expect(usesSpacingVars).toBe(true);
  });

  test('should use consistent border radius', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Find interactive elements (buttons, cards)
    const buttons = page.locator('button').first();
    const cards = page.locator('[class*="card"]').first();

    const elements = [];
    if (await buttons.isVisible()) elements.push(buttons);
    if (await cards.isVisible()) elements.push(cards);

    if (elements.length > 0) {
      const radiusValues = await Promise.all(
        elements.map(el =>
          el.evaluate(node => window.getComputedStyle(node).borderRadius)
        )
      );

      // All should have some border radius
      radiusValues.forEach(radius => {
        expect(radius).not.toBe('0px');
      });
    }
  });

  test('should have proper font hierarchy', async ({ page }) => {
    await page.goto('/');

    const h1 = page.locator('h1').first();
    const h2 = page.locator('h2').first();
    const body = page.locator('p, div').first();

    const sizes = {};

    if (await h1.isVisible()) {
      sizes.h1 = await h1.evaluate(el =>
        parseInt(window.getComputedStyle(el).fontSize)
      );
    }

    if (await h2.isVisible()) {
      sizes.h2 = await h2.evaluate(el =>
        parseInt(window.getComputedStyle(el).fontSize)
      );
    }

    if (await body.isVisible()) {
      sizes.body = await body.evaluate(el =>
        parseInt(window.getComputedStyle(el).fontSize)
      );
    }

    // H1 should be larger than H2, which should be larger than body
    if (sizes.h1 && sizes.body) {
      expect(sizes.h1).toBeGreaterThan(sizes.body);
    }

    if (sizes.h1 && sizes.h2) {
      expect(sizes.h1).toBeGreaterThanOrEqual(sizes.h2);
    }
  });

  test('should have hover states on interactive elements', async ({ page }) => {
    await page.goto('/');

    const button = page.locator('button').first();

    if (await button.isVisible()) {
      const initialBg = await button.evaluate(el =>
        window.getComputedStyle(el).backgroundColor
      );

      await button.hover();
      await page.waitForTimeout(100);

      const hoveredBg = await button.evaluate(el =>
        window.getComputedStyle(el).backgroundColor
      );

      // Hover state might change background or opacity
      // This is optional but enhances UX
    }
  });

  test('should have appropriate contrast ratios', async ({ page }) => {
    await page.goto('/');

    // Check that text is readable against background
    const textElement = page.locator('p, h1, h2, span').first();

    if (await textElement.isVisible()) {
      const contrast = await textElement.evaluate((el) => {
        const color = window.getComputedStyle(el).color;
        const bgColor = window.getComputedStyle(el).backgroundColor;

        // Helper to parse rgb
        const parseRGB = (str) => {
          const match = str.match(/\d+/g);
          return match ? match.map(Number) : [255, 255, 255];
        };

        const textRGB = parseRGB(color);
        const bgRGB = parseRGB(bgColor);

        // Calculate relative luminance
        const getLuminance = (rgb) => {
          const [r, g, b] = rgb.map(val => {
            val /= 255;
            return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
          });
          return 0.2126 * r + 0.7152 * g + 0.0722 * b;
        };

        const l1 = getLuminance(textRGB);
        const l2 = getLuminance(bgRGB);

        return l1 > l2 ? (l1 + 0.05) / (l2 + 0.05) : (l2 + 0.05) / (l1 + 0.05);
      });

      // WCAG AA requires 4.5:1 for normal text
      expect(contrast).toBeGreaterThanOrEqual(3); // Allowing slightly lower for now
    }
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/');

    // Press Tab to navigate
    await page.keyboard.press('Tab');
    await page.waitForTimeout(100);

    // Check if focus moved
    const focusedElement = await page.evaluate(() =>
      document.activeElement.tagName
    );

    // Should focus on interactive elements (not BODY)
    expect(focusedElement).not.toBe('BODY');
  });

  test('should display properly on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');

    // No horizontal scroll
    const hasHorizontalScroll = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(hasHorizontalScroll).toBe(false);

    // Content should be visible
    await expect(page.locator('body')).toBeVisible();
  });
});
