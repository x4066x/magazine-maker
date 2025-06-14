import { test, expect } from '@playwright/test';

test.describe('ラクスル自動注文テスト', () => {
  test.beforeEach(async ({ page }) => {
    // ラクスルのログインページにアクセス
    await page.goto('https://raksul.com/login');
    // ページの読み込みを待機
    await page.waitForLoadState('networkidle');
  });

  test('ログインから雑誌注文までの一連のフロー', async ({ page }) => {
    // ログイン処理
    await page.waitForSelector('input[type="email"]');
    await page.fill('input[type="email"]', process.env.RAKSUL_EMAIL || '');
    await page.fill('input[type="password"]', process.env.RAKSUL_PASSWORD || '');
    await page.click('button:has-text("ログイン")');

    // ログイン後のページ読み込みを待機
    await page.waitForURL('https://raksul.com/');
    await page.waitForLoadState('networkidle');

    // 雑誌注文ページに移動
    await page.goto('https://raksul.com/products/magazine');
    await page.waitForLoadState('networkidle');

    // 注文フォームの入力
    // TODO: 実際のフォーム要素に合わせて実装
    await page.fill('input[name="title"]', 'テスト雑誌');
    await page.fill('input[name="quantity"]', '100');
    
    // 注文確認
    await page.click('button:has-text("注文する")');

    // 注文完了の確認
    await expect(page.locator('.order-complete')).toBeVisible();
  });

  test('ログインページの要素確認', async ({ page }) => {
    // ラクスルのログインページにアクセス
    await page.goto('https://raksul.com/login');
    await page.waitForLoadState('networkidle');

    // ページのタイトルを確認
    const title = await page.title();
    console.log('ページタイトル:', title);

    // ログインフォームの要素を確認
    const emailInput = await page.locator('input[type="email"]');
    const passwordInput = await page.locator('input[type="password"]');
    const loginButton = await page.locator('button:has-text("ログイン")');

    console.log('メールアドレス入力欄の存在:', await emailInput.isVisible());
    console.log('パスワード入力欄の存在:', await passwordInput.isVisible());
    console.log('ログインボタンの存在:', await loginButton.isVisible());

    // 要素の属性を確認
    if (await emailInput.isVisible()) {
      console.log('メールアドレス入力欄の属性:', await emailInput.getAttribute('name'));
    }
    if (await passwordInput.isVisible()) {
      console.log('パスワード入力欄の属性:', await passwordInput.getAttribute('name'));
    }
  });

  test('雑誌注文ページの要素確認', async ({ page }) => {
    // 雑誌注文ページにアクセス
    await page.goto('https://raksul.com/products/magazine');
    await page.waitForLoadState('networkidle');

    // ページのタイトルを確認
    const title = await page.title();
    console.log('雑誌注文ページのタイトル:', title);

    // 注文フォームの要素を確認
    const formElements = await page.locator('form').all();
    console.log('フォームの数:', formElements.length);

    // 各フォームの入力要素を確認
    for (const form of formElements) {
      const inputs = await form.locator('input').all();
      console.log('フォーム内の入力要素数:', inputs.length);
      for (const input of inputs) {
        const name = await input.getAttribute('name');
        const type = await input.getAttribute('type');
        console.log('入力要素:', { name, type });
      }
    }
  });
}); 