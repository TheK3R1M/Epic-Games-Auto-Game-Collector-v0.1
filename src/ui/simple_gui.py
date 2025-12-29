# Simple GUI - basic graphical interface
import PySimpleGUI as sg
from src.core import AccountManager, GameClaimer
import asyncio
import threading


class SimpleGUI:
    """Basic interface using PySimpleGUI."""
    
    def __init__(self):
        sg.theme('DarkBlue3')
        self.manager = AccountManager()
        self.running = False
    
    def show_add_account_window(self):
        """Account add dialog."""
        layout = [
            [sg.Text('Add Epic Games Account', font=('Arial', 14, 'bold'))],
            [sg.Text('Email:'), sg.Input(key='email', size=(30, 1))],
            [sg.Text('Password:'), sg.Input(key='password', password_char='*', size=(30, 1))],
            [sg.Button('Add'), sg.Button('Cancel')]
        ]
        
        window = sg.Window('Add Account', layout)
        
        while True:
            event, values = window.read()
            
            if event == sg.WINDOW_CLOSED or event == 'Cancel':
                break
            
            if event == 'Add':
                email = values['email'].strip()
                password = values['password'].strip()
                
                if email and password:
                    try:
                        self.manager.add_account(email, password)
                        sg.popup_ok('✅ Account added successfully!', title='Success')
                        break
                    except Exception as e:
                        sg.popup_error(f'❌ Error: {str(e)}', title='Error')
                else:
                    sg.popup_warning('Please enter email and password!', title='Warning')
        
        window.close()
    
    def show_accounts_window(self):
        """List accounts."""
        accounts = self.manager.get_all_accounts()
        
        if not accounts:
            sg.popup_info('No accounts added.', title='Accounts')
            return
        
        account_list = []
        for i, acc in enumerate(accounts, 1):
            status = acc.get('status', 'unknown')
            claimed = len(acc.get('claimed_games', []))
            account_list.append(f"{i}. {acc['email']} - Status: {status} - Claimed: {claimed}")
        
        layout = [
            [sg.Text('Saved Accounts', font=('Arial', 14, 'bold'))],
            [sg.Listbox(account_list, size=(50, 10), key='accounts')],
            [sg.Button('Delete'), sg.Button('Close')]
        ]
        
        window = sg.Window('Accounts', layout)
        
        while True:
            event, values = window.read()
            
            if event == sg.WINDOW_CLOSED or event == 'Close':
                break
            
            if event == 'Delete':
                if values['accounts']:
                    selected = values['accounts'][0]
                    # extract email
                    email = selected.split(' - ')[0].split('. ')[1]
                    
                    if sg.popup_yes_no(f"Are you sure you want to delete '{email}'?") == 'Yes':
                        self.manager.remove_account(email)
                        sg.popup_ok('✅ Account deleted!', title='Success')
                        break
                else:
                    sg.popup_warning('Select an account!', title='Warning')
        
        window.close()
    
    def show_claim_window(self):
        """Game claim dialog."""
        accounts = self.manager.get_all_accounts()
        
        if not accounts:
            sg.popup_info('No accounts added. Please add accounts first.', title='Warning')
            return
        
        layout = [
            [sg.Text('Claim Games', font=('Arial', 14, 'bold'))],
            [sg.Checkbox('Claim for all accounts', key='all_accounts', default=True)],
            [sg.Multiline(size=(60, 15), key='output', disabled=True)],
            [sg.Button('Start'), sg.Button('Close')]
        ]
        
        window = sg.Window('Claim Games', layout)
        
        while True:
            event, values = window.read()
            
            if event == sg.WINDOW_CLOSED or event == 'Close':
                break
            
            if event == 'Start':
                # start claim process
                self._run_game_claimer(window, values['output'] + '')
        
        window.close()
    
    def _run_game_claimer(self, window, output_key):
        """Run game claim flow in background."""
        def run_async():
            claimer = GameClaimer()
            try:
                results = asyncio.run(claimer.claim_free_games_for_all_accounts())
                
                # show results
                message = "\n✅ Completed!\n\n"
                total_claimed = 0
                
                for result in results:
                    message += f"📧 {result['email']}\n"
                    message += f"   Status: {result['status']}\n"
                    message += f"   Claimed: {len(result['claimed_games'])}\n"
                    total_claimed += len(result['claimed_games'])
                
                message += f"\n📈 Total Claimed: {total_claimed}"
                sg.popup_ok(message, title='Results')
            
            except Exception as e:
                sg.popup_error(f'❌ Error: {str(e)}', title='Error')
        
        # run in thread
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
    
    def run(self):
        """Run main window."""
        while True:
            layout = [
                [sg.Text('🎮 Epic Games - Auto Game Collector', font=('Arial', 16, 'bold'))],
                [sg.Text('')],
                [sg.Button('➕ Add Account', size=(20, 2), button_color=('white', 'green'))],
                [sg.Button('📋 List Accounts', size=(20, 2), button_color=('white', 'blue'))],
                [sg.Button('🗑️ Delete Account', size=(20, 2), button_color=('white', 'red'))],
                [sg.Button('🎁 Claim Games', size=(20, 2), button_color=('white', 'purple'))],
                [sg.Text('')],
                [sg.Button('❌ Exit', size=(20, 2), button_color=('white', 'gray'))],
            ]
            
            window = sg.Window('Epic Games Collector', layout, finalize=True)
            
            while True:
                event, values = window.read()
                
                if event == sg.WINDOW_CLOSED or event == '❌ Exit':
                    window.close()
                    return
                
                window.close()
                
                if event == '➕ Add Account':
                    self.show_add_account_window()
                elif event == '📋 List Accounts':
                    self.show_accounts_window()
                elif event == '🗑️ Delete Account':
                    self.show_accounts_window()  # Listele ve sil seçeneği
                elif event == '🎁 Claim Games':
                    self.show_claim_window()
                
                break


if __name__ == "__main__":
    gui = SimpleGUI()
    gui.run()
