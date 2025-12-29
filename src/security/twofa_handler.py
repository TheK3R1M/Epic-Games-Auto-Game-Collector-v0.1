# 2FA Handler - two-factor authentication
import asyncio
import time
from typing import Optional


class TwoFactorHandler:
    """Handle two-factor authentication flows."""
    
    def __init__(self):
        self.otp_input_selector = "input[data-testid='mfa-code-input']"
        self.email_code_selector = "input[data-testid='email-code-input']"
        self.sms_code_selector = "input[data-testid='sms-code-input']"
    
    async def handle_2fa(self, page, method: str = "manual") -> bool:
        """
        Handle 2FA.

        method: 'manual', 'totp', 'email', 'sms'
        """
        try:
            print("🔐 2FA verification required")
            
            # 2FA sayfasının açılmasını bekle
            await asyncio.sleep(2)
            
            # 2FA metodunu kontrol et
            if method == "manual":
                return await self._manual_2fa(page)
            elif method == "totp":
                return await self._totp_2fa(page)
            elif method == "email":
                return await self._email_2fa(page)
            elif method == "sms":
                return await self._sms_2fa(page)
            else:
                print("❌ Unknown 2FA method")
                return False
        
        except Exception as e:
            print(f"❌ 2FA error: {str(e)}")
            return False
    
    async def _manual_2fa(self, page) -> bool:
        """
        Prompt user for code manually.
        """
        try:
            print("\n📱 Please enter your 2FA code:")
            print("(Find it in your authenticator/phone)")
            
            # Kod gir
            code = input("2FA code: ").strip()
            
            if len(code) < 4:
                print("❌ Invalid code")
                return False
            
            # OTP input'unu bul ve kodu gir
            otp_input = await page.query_selector(self.otp_input_selector)
            if otp_input:
                await otp_input.fill(code)
                await asyncio.sleep(1)
                
                # click verify
                verify_button = await page.query_selector("button:has-text('Verify')")
                if verify_button:
                    await verify_button.click()
                    await asyncio.sleep(3)
                    
                    # check success
                    if "Dashboard" in await page.title() or await self._check_login_success(page):
                        print("✅ 2FA success")
                        return True
                    else:
                        print("❌ 2FA code incorrect")
                        return False
            
            return False
        
        except Exception as e:
            print(f"❌ Manual 2FA error: {str(e)}")
            return False
    
    async def _totp_2fa(self, page) -> bool:
        """
        TOTP (Time-based One-Time Password) 2FA.

        Note: requires pyotp.
        """
        try:
            print("⏰ TOTP 2FA method")
            print("Note: requires authenticator app")
            
            # fall back to manual code prompt
            return await self._manual_2fa(page)
        
        except Exception as e:
            print(f"❌ TOTP 2FA error: {str(e)}")
            return False
    
    async def _email_2fa(self, page) -> bool:
        """
        Email-based 2FA.
        """
        try:
            print("📧 Email 2FA method")
            print("Epic Games sent you a verification code")
            
            code = input("Enter the email code: ").strip()
            
            if len(code) < 4:
                print("❌ Invalid code")
                return False
            
            # locate email input - try multiple selectors
            email_input = None
            selectors = [
                self.email_code_selector,
                "input[data-testid='email-code-input']",
                "input[name='code']",
                "input[name='verificationCode']",
                "input[type='text'][placeholder*='code' i]",
                "input[type='text'][placeholder*='Code' i]",
                "input[type='text'][id*='code' i]",
            ]
            
            for selector in selectors:
                try:
                    email_input = await page.query_selector(selector)
                    if email_input:
                        print(f"   ✓ Email input found: {selector}")
                        break
                except:
                    pass
            
            # fallback to first text input
            if not email_input:
                all_inputs = await page.query_selector_all("input[type='text']")
                if all_inputs:
                    email_input = all_inputs[0]
                    print(f"   ✓ Using first text input")
            
            if email_input:
                print(f"   📝 Entering code: {code}")
                await email_input.fill(code)
                await asyncio.sleep(1)
                
                # click verify/confirm/submit
                verify_button = None
                buttons = await page.query_selector_all("button")
                for btn in buttons:
                    text = (await btn.text_content() or "").strip().lower()
                    if any(x in text for x in ["verify", "confirm", "submit", "continue", "next", "doğrula"]):
                        verify_button = btn
                        print(f"   ✓ Verification button found: {text}")
                        break
                
                if verify_button:
                    await verify_button.click()
                    await asyncio.sleep(3)
                    
                    if await self._check_login_success(page):
                        print("✅ Email 2FA success")
                        return True
                else:
                    print("   ⚠️ Verification button not found, trying Enter...")
                    await email_input.press("Enter")
                    await asyncio.sleep(3)
                    if await self._check_login_success(page):
                        print("✅ Email 2FA success")
                        return True
            else:
                print("❌ Email input not found")
            
            return False
        
        except Exception as e:
            print(f"❌ Email 2FA error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def _sms_2fa(self, page) -> bool:
        """SMS 2FA (phone code)."""
        try:
            print("📱 SMS 2FA method")
            print("Enter the code sent to your phone")

            code = input("SMS code: ").strip()
            if len(code) < 4:
                print("❌ Invalid code")
                return False

            sms_input = None
            selectors = [
                self.sms_code_selector,
                "input[name='code']",
                "input[name='verificationCode']",
                "input[type='text'][placeholder*='code' i]",
                "input[type='text'][id*='code' i]",
            ]
            for selector in selectors:
                try:
                    sms_input = await page.query_selector(selector)
                    if sms_input:
                        print(f"   ✓ SMS input found: {selector}")
                        break
                except:
                    pass

            if not sms_input:
                all_inputs = await page.query_selector_all("input[type='text']")
                if all_inputs:
                    sms_input = all_inputs[0]
                    print("   ✓ Using first text input")

            if sms_input:
                await sms_input.fill(code)
                await asyncio.sleep(1)
                verify_button = None
                buttons = await page.query_selector_all("button")
                for btn in buttons:
                    text = (await btn.text_content() or "").strip().lower()
                    if any(x in text for x in ["verify", "confirm", "submit", "continue", "next", "doğrula"]):
                        verify_button = btn
                        break
                if verify_button:
                    await verify_button.click()
                    await asyncio.sleep(3)
                    if await self._check_login_success(page):
                        print("✅ SMS 2FA success")
                        return True
                else:
                    await sms_input.press("Enter")
                    await asyncio.sleep(3)
                    if await self._check_login_success(page):
                        print("✅ SMS 2FA success")
                        return True
            else:
                print("❌ SMS input not found")
            return False

        except Exception as e:
            print(f"❌ SMS 2FA error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _check_login_success(self, page) -> bool:
        """Check if login succeeded."""
        try:
            # possible success indicators
            success_indicators = [
                "Dashboard",
                "Profile",
                "/store",
                "/account"
            ]
            
            current_url = page.url
            page_title = await page.title()
            
            for indicator in success_indicators:
                if indicator.lower() in current_url.lower() or indicator.lower() in page_title.lower():
                    return True
            
            # check error messages
            error_elements = await page.query_selector_all("[class*='error'], [class*='Error']")
            if error_elements:
                return False
            
            return True
        
        except:
            return False
    
    async def detect_2fa_requirement(self, page) -> Optional[str]:
        """
        Detect whether 2FA is required and which method.
        """
        try:
            page_content = await page.content()
            
            # check possible 2FA types
            if "authenticator" in page_content.lower() or "totp" in page_content.lower():
                return "totp"
            elif "email" in page_content.lower() and "code" in page_content.lower():
                return "email"
            elif "sms" in page_content.lower() or "phone" in page_content.lower():
                return "sms"
            elif "verification" in page_content.lower() or "verify" in page_content.lower():
                return "manual"
            
            # fallback: look for OTP input
            otp_input = await page.query_selector(self.otp_input_selector)
            if otp_input:
                return "manual"
            
            return None
        
        except:
            return None
