import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ProfessionalAccountingSystem:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.journal_entries = []
        self.accounts = {}
        self.load_data()
        
    def load_data(self):
        """تحميل البيانات من ملف Excel"""
        try:
            self.df = pd.read_excel(self.file_path)
            print("✅ تم تحميل البيانات بنجاح")
            self.clean_data()
        except Exception as e:
            print(f"❌ خطأ في تحميل الملف: {e}")
    
    def clean_data(self):
        """تنظيف البيانات ومعالجتها"""
        # تحويل التواريخ
        self.df['[SA]Processing Date'] = pd.to_datetime(self.df['[SA]Processing Date'])
        
        # تنظيف الأعمدة النقدية
        self.df['مدين'] = pd.to_numeric(self.df['مدين'], errors='coerce').fillna(0)
        self.df['دائن'] = pd.to_numeric(self.df['دائن'], errors='coerce').fillna(0)
        self.df['الرصيد'] = pd.to_numeric(self.df['الرصيد'], errors='coerce').fillna(0)
        
        # إضافة أعمدة مساعدة
        self.df['الشهر'] = self.df['[SA]Processing Date'].dt.month
        self.df['السنة'] = self.df['[SA]Processing Date'].dt.year
        
    def classify_transactions(self):
        """تصنيف الحركات إلى حسابات محاسبية"""
        account_mapping = {
            'تحويل داخلي صادر': 'مصاريف تشغيل',
            'حوالة فورية محلية صادرة': 'مصاريف مشتريات',
            'ضريبة القيمة المضافة': 'مصاريف ضرائب',
            'رسوم تحويل': 'مصاريف بنكية',
            'مدفوعات سداد': 'مصاريف سداد قروض',
            'شراء محلي عبر الإنترنت': 'مصاريف مشتريات',
            'حوالة محلية واردة': 'إيرادات عمليات',
            'حوالة فورية محلية واردة': 'إيرادات عمليات',
            'استرداد عملية سداد': 'إيرادات متنوعة',
            'سحب نقدي بالريال - صراف الأهلي': 'سحوبات نقدية',
            'تحويل داخلي وارد': 'إيرادات تحويلات'
        }
        
        self.df['الحساب المحاسبي'] = self.df['التفاصيل'].map(account_mapping)
        self.df['الحساب المحاسبي'] = self.df['الحساب المحاسبي'].fillna('حسابات متنوعة')
        
    def create_journal_entries(self):
        """إنشاء قيود اليومية"""
        print("\n📖 جاري إنشاء قيود اليومية...")
        
        for index, row in self.df.iterrows():
            date = row['[SA]Processing Date']
            description = row['التفاصيل']
            debit = row['مدين']
            credit = row['دائن']
            account = row['الحساب المحاسبي']
            
            if debit > 0:
                # قيد مدين
                entry = {
                    'التاريخ': date,
                    'الحساب المدين': account,
                    'المبلغ المدين': debit,
                    'الحساب الدائن': 'البنك',
                    'المبلغ الدائن': 0,
                    'الوصف': description
                }
                self.journal_entries.append(entry)
                
            if credit > 0:
                # قيد دائن
                entry = {
                    'التاريخ': date,
                    'الحساب المدين': 'البنك',
                    'المبلغ المدين': 0,
                    'الحساب الدائن': account,
                    'المبلغ الدائن': credit,
                    'الوصف': description
                }
                self.journal_entries.append(entry)
        
        journal_df = pd.DataFrame(self.journal_entries)
        return journal_df
    
    def generate_trial_balance(self):
        """إنشاء ميزان المراجعة"""
        print("\n⚖️ جاري إنشاء ميزان المراجعة...")
        
        trial_balance = {}
        
        for entry in self.journal_entries:
            debit_account = entry['الحساب المدين']
            credit_account = entry['الحساب الدائن']
            debit_amount = entry['المبلغ المدين']
            credit_amount = entry['المبلغ الدائن']
            
            # تحديث الحسابات المدينة
            if debit_account not in trial_balance:
                trial_balance[debit_account] = {'مدين': 0, 'دائن': 0}
            trial_balance[debit_account]['مدين'] += debit_amount
            
            # تحديث الحسابات الدائنة
            if credit_account not in trial_balance:
                trial_balance[credit_account] = {'مدين': 0, 'دائن': 0}
            trial_balance[credit_account]['دائن'] += credit_amount
        
        # تحويل إلى DataFrame
        tb_data = []
        for account, balances in trial_balance.items():
            tb_data.append({
                'الحساب': account,
                'مجموع المدين': balances['مدين'],
                'مجموع الدائن': balances['دائن'],
                'الرصيد': balances['مدين'] - balances['دائن']
            })
        
        trial_balance_df = pd.DataFrame(tb_data)
        return trial_balance_df
    
    def generate_income_statement(self):
        """إنشاء قائمة الدخل"""
        print("\n📈 جاري إنشاء قائمة الدخل...")
        
        # تجميع الإيرادات
        revenue_accounts = ['إيرادات عمليات', 'إيرادات تحويلات', 'إيرادات متنوعة']
        total_revenue = self.df[self.df['الحساب المحاسبي'].isin(revenue_accounts)]['دائن'].sum()
        
        # تجميع المصروفات
        expense_accounts = ['مصاريف تشغيل', 'مصاريف مشتريات', 'مصاريف ضرائب', 'مصاريف بنكية', 'مصاريف سداد قروض']
        total_expenses = self.df[self.df['الحساب المحاسبي'].isin(expense_accounts)]['مدين'].sum()
        
        net_income = total_revenue - total_expenses
        
        income_statement = {
            'الإيرادات': {
                'إيرادات العمليات': self.df[self.df['الحساب المحاسبي'] == 'إيرادات عمليات']['دائن'].sum(),
                'إيرادات التحويلات': self.df[self.df['الحساب المحاسبي'] == 'إيرادات تحويلات']['دائن'].sum(),
                'إيرادات متنوعة': self.df[self.df['الحساب المحاسبي'] == 'إيرادات متنوعة']['دائن'].sum(),
                'إجمالي الإيرادات': total_revenue
            },
            'المصروفات': {
                'مصاريف تشغيل': self.df[self.df['الحساب المحاسبي'] == 'مصاريف تشغيل']['مدين'].sum(),
                'مصاريف مشتريات': self.df[self.df['الحساب المحاسبي'] == 'مصاريف مشتريات']['مدين'].sum(),
                'مصاريف ضرائب': self.df[self.df['الحساب المحاسبي'] == 'مصاريف ضرائب']['مدين'].sum(),
                'مصاريف بنكية': self.df[self.df['الحساب المحاسبي'] == 'مصاريف بنكية']['مدين'].sum(),
                'مصاريف سداد قروض': self.df[self.df['الحساب المحاسبي'] == 'مصاريف سداد قروض']['مدين'].sum(),
                'إجمالي المصروفات': total_expenses
            },
            'صافي الدخل': net_income
        }
        
        return income_statement
    
    def generate_cash_flow_statement(self):
        """إنشاء قائمة التدفقات النقدية"""
        print("\n💸 جاري إنشاء قائمة التدفقات النقدية...")
        
        # التدفقات من الأنشطة التشغيلية
        operating_activities = self.df[self.df['الحساب المحاسبي'].isin([
            'إيرادات عمليات', 'مصاريف تشغيل', 'مصاريف مشتريات'
        ])]
        
        cash_from_operations = (
            operating_activities['دائن'].sum() - 
            operating_activities['مدين'].sum()
        )
        
        # التدفقات من الأنشطة التمويلية
        financing_activities = self.df[self.df['الحساب المحاسبي'].isin([
            'مصاريف سداد قروض', 'إيرادات تحويلات'
        ])]
        
        cash_from_financing = (
            financing_activities['دائن'].sum() - 
            financing_activities['مدين'].sum()
        )
        
        # صافي التغير في النقد
        net_cash_change = self.df['دائن'].sum() - self.df['مدين'].sum()
        
        cash_flow_statement = {
            'التدفقات النقدية من الأنشطة التشغيلية': cash_from_operations,
            'التدفقات النقدية من الأنشطة التمويلية': cash_from_financing,
            'صافي الزيادة (النقص) في النقد': net_cash_change,
            'الرصيد النقدي في بداية الفترة': self.df['الرصيد'].iloc[-1] - net_cash_change,
            'الرصيد النقدي في نهاية الفترة': self.df['الرصيد'].iloc[-1]
        }
        
        return cash_flow_statement
    
    def generate_balance_sheet(self):
        """إنشاء الميزانية العمومية"""
        print("\n🏦 جاري إنشاء الميزانية العمومية...")
        
        # الأصول
        cash_balance = self.df['الرصيد'].iloc[-1]
        
        # الخصوم وحقوق الملكية
        net_income = self.generate_income_statement()['صافي الدخل']
        
        balance_sheet = {
            'الأصول': {
                'النقد والبنك': cash_balance,
                'إجمالي الأصول': cash_balance
            },
            'الخصوم': {
                'إجمالي الخصوم': 0  # يمكن إضافة الخصوم المستقبلية
            },
            'حقوق الملكية': {
                'صافي الدخل': net_income,
                'إجمالي حقوق الملكية': net_income
            }
        }
        
        # المعادلة المحاسبية: الأصول = الخصوم + حقوق الملكية
        balance_sheet['الخصوم']['إجمالي الخصوم'] = cash_balance - net_income
        
        return balance_sheet
    
    def generate_expense_analysis(self):
        """تحليل المصروفات التفصيلي"""
        print("\n📊 جاري إنشاء تحليل المصروفات...")
        
        expense_analysis = self.df[self.df['مدين'] > 0].groupby('الحساب المحاسبي').agg({
            'مدين': ['sum', 'count', 'mean'],
            'الرصيد': 'last'
        }).round(2)
        
        return expense_analysis
    
    def generate_revenue_analysis(self):
        """تحليل الإيرادات التفصيلي"""
        print("\n📈 جاري إنشاء تحليل الإيرادات...")
        
        revenue_analysis = self.df[self.df['دائن'] > 0].groupby('الحساب المحاسبي').agg({
            'دائن': ['sum', 'count', 'mean'],
            'الرصيد': 'last'
        }).round(2)
        
        return revenue_analysis
    
    def generate_monthly_reports(self):
        """إنشاء تقارير شهرية"""
        print("\n📅 جاري إنشاء التقارير الشهرية...")
        
        monthly_data = self.df.groupby(['السنة', 'الشهر']).agg({
            'مدين': 'sum',
            'دائن': 'sum',
            'الرصيد': 'last'
        }).reset_index()
        
        return monthly_data
    
    def generate_comprehensive_report(self):
        """إنشاء التقرير المالي الشامل"""
        print("🚀 بدء إنشاء التقرير المالي الشامل...")
        
        # تصنيف الحركات أولاً
        self.classify_transactions()
        
        # إنشاء جميع التقارير
        reports = {
            'قيود_اليومية': self.create_journal_entries(),
            'ميزان_المراجعة': self.generate_trial_balance(),
            'قائمة_الدخل': self.generate_income_statement(),
            'قائمة_التدفقات_النقدية': self.generate_cash_flow_statement(),
            'الميزانية_العمومية': self.generate_balance_sheet(),
            'تحليل_المصروفات': self.generate_expense_analysis(),
            'تحليل_الإيرادات': self.generate_revenue_analysis(),
            'التقارير_الشهرية': self.generate_monthly_reports()
        }
        
        print("✅ تم إنشاء جميع التقارير بنجاح!")
        return reports
    
    def save_reports_to_excel(self, reports, output_path):
        """حفظ جميع التقارير في ملف Excel واحد"""
        print(f"\n💾 جاري حفظ التقارير في: {output_path}")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # حفظ قيود اليومية
            reports['قيود_اليومية'].to_excel(writer, sheet_name='قيود اليومية', index=False)
            
            # حفظ ميزان المراجعة
            reports['ميزان_المراجعة'].to_excel(writer, sheet_name='ميزان المراجعة', index=False)
            
            # حفظ قائمة الدخل
            income_data = []
            for category, items in reports['قائمة_الدخل'].items():
                if isinstance(items, dict):
                    for item, value in items.items():
                        income_data.append({'البند': item, 'المبلغ': value})
                else:
                    income_data.append({'البند': category, 'المبلغ': items})
            pd.DataFrame(income_data).to_excel(writer, sheet_name='قائمة الدخل', index=False)
            
            # حفظ قائمة التدفقات النقدية
            cash_flow_data = []
            for item, value in reports['قائمة_التدفقات_النقدية'].items():
                cash_flow_data.append({'البند': item, 'المبلغ': value})
            pd.DataFrame(cash_flow_data).to_excel(writer, sheet_name='التدفقات النقدية', index=False)
            
            # حفظ الميزانية العمومية
            balance_data = []
            for section, items in reports['الميزانية_العمومية'].items():
                balance_data.append({'القسم': section, '': ''})
                for item, value in items.items():
                    balance_data.append({'القسم': item, 'المبلغ': value})
            pd.DataFrame(balance_data).to_excel(writer, sheet_name='الميزانية العمومية', index=False)
            
            # حفظ التحليلات
            reports['تحليل_المصروفات'].to_excel(writer, sheet_name='تحليل المصروفات')
            reports['تحليل_الإيرادات'].to_excel(writer, sheet_name='تحليل الإيرادات')
            reports['التقارير_الشهرية'].to_excel(writer, sheet_name='التقارير الشهرية', index=False)
        
        print(f"✅ تم حفظ جميع التقارير في: {output_path}")

# استخدام البرنامج
def main():
    # استبدل المسار بمسار ملفك
    file_path = "bank1 (1).xlsx"
    
    # إنشاء النظام المحاسبي
    accounting_system = ProfessionalAccountingSystem(file_path)
    
    # إنشاء التقارير الشاملة
    reports = accounting_system.generate_comprehensive_report()
    
    # حفظ التقارير في ملف Excel
    output_path = "التقارير_المالية_الشاملة.xlsx"
    accounting_system.save_reports_to_excel(reports, output_path)
    
    print("\n🎉 تم الانتهاء من إنشاء النظام المحاسبي المتكامل!")
    print("📁 يمكنك العثور على جميع التقارير في ملف: التقارير_المالية_الشاملة.xlsx")

if __name__ == "__main__":
    main()