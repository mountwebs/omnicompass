import { test, expect } from '@playwright/test';

test('check console logs for arrow loading', async ({ page }) => {
  page.on('console', msg => console.log(`PAGE LOG: ${msg.text()}`));
  page.on('pageerror', exception => console.log(`PAGE ERROR: ${exception}`));

  await page.goto('http://localhost:5174');
  
  // Wait for a bit to allow loading
  await page.waitForTimeout(5000);
  
  await page.screenshot({ path: 'debug_arrow.png' });
  
  // Check if the arrow is in the scene (we can't easily check 3D object existence via DOM, 
  // but we can check if the canvas exists and if logs appeared)
  const canvas = page.locator('canvas');
  await expect(canvas).toBeVisible();
});
