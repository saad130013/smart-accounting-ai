import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# إعداد صفحة Streamlit
st.set_page_config(page_title="المحاسب الذكي", page_icon="🏦", layout="wide")

st.title("🏦 النظام المحاسبي المتكامل")
st.markdown("---")

class ProfessionalAccountingSystem:
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self.df = None
        self.journal_entries = []
        self.accounts = {}
        self.load_data()
        
    def load_data(self):
        """تحميل البيانات من الملف المرفوع"""
        try:
            self.df = pd.read_excel(self.uploaded_file)
            st.success("✅ تم تحميل البيانات بنجاح")
            st.info(f"📊 عدد الحركات: {len(self.df)}")
            self.clean_data()
        except Exception as e:
            st.error(f"❌ خطأ في تحميل الملف: {e}")
    
    def clean_data(self):
        """تنظيف البيانات ومعالجتها"""
        # تحويل التواريخ
        self.df['[SA]Processing Date'] = pd.to_datetime(self.df['[SA]Processing Date'], errors='coerce')
        
        # تنظيف الأعمدة النقدية
        numeric_columns = ['مدين', 'دائن', 'الرصيد']
        for col in numeric_columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
        
        # إضافة أعمدة مساعدة
        self.df['الشهر'] = self.df['[SA]Processing Date'].dt.month
        self.df['السنة'] = self.df['[SA]Processing Date'].dt.year
        
        st.success("✅ تم تنظيف البيانات بنجاح")
    
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
        with st.spinner('📖 جاري إنشاء قيود اليومية...'):
            for index, row in self.df.iterrows():
                date = row['[SA]Processing Date']
                description = row['التفاصيل']
                debit = row['مدين']
                credit = row['دائن']
                account = row.get('الحساب المحاسبي', 'حسابات متنوعة')
                
                if debit > 0:
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
        with st.spinner('⚖️ جاري إنشاء ميزان المراجعة...'):
            if not self.journal_entries:
                self.create_journal_entries()
            
            trial_balance = {}
            
            for entry in self.journal_entries:
                debit_account = entry['الحساب المدين']
                credit_account = entry['الحساب الدائن']
                debit_amount = entry['المبلغ المدين']
                credit_amount = entry['المبلغ الدائن']
                
                if debit_account not in trial_balance:
                    trial_balance[debit_account] = {'مدين': 0, 'دائن': 0}
                trial_balance[debit_account]['مدين'] += debit_amount
                
                if credit_account not in trial_balance:
                    trial_balance[credit_account] = {'مدين': 0, 'دائن': 0}
                trial_balance[credit_account]['دائن'] += credit_amount
            
            tb_data = []
            for account, balances in trial_balance.items():
                balance = balances['مدين'] - balances['دائن']
                tb_data.append({
                    'الحساب': account,
                    'مجموع المدين': balances['مدين'],
                    'مجموع الدائن': balances['دائن'],
                    'الرصيد': balance
                })
            
            trial_balance_df = pd.DataFrame(tb_data)
            return trial_balance_df
    
    def generate_income_statement(self):
        """إنشاء قائمة الدخل"""
        with st.spinner('📈 جاري إنشاء قائمة الدخل...'):
            revenue_accounts = ['إيرادات عمليات', 'إيرادات تحويلات', 'إيرادات متنوعة']
            total_revenue = self.df[self.df['الحساب المحاسبي'].isin(revenue_accounts)]['دائن'].sum()
            
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
        with st.spinner('💸 جاري إنشاء قائمة التدفقات النقدية...'):
            operating_activities = self.df[self.df['الحساب المحاسبي'].isin([
                'إيرادات عمليات', 'مصاريف تشغيل', 'مصاريف مشتريات'
            ])]
            
            cash_from_operations = (
                operating_activities['دائن'].sum() - 
                operating_activities['مدين'].sum()
            )
            
            financing_activities = self.df[self.df['الحساب المحاسبي'].isin([
                'مصاريف سداد قروض', 'إيرادات تحويلات'
            ])]
            
            cash_from_financing = (
                financing_activities['دائن'].sum() - 
                financing_activities['مدين'].sum()
            )
            
            net_cash_change = self.df['دائن'].sum() - self.df['مدين'].sum()
            opening_balance = self.df['الرصيد'].iloc[-1] - net_cash_change
            
            cash_flow_statement = {
                'التدفقات النقدية من الأنشطة التشغيلية': cash_from_operations,
                'التدفقات النقدية من الأنشطة التمويلية': cash_from_financing,
                'صافي الزيادة (النقص) في النقد': net_cash_change,
                'الرصيد النقدي في بداية الفترة': opening_balance,
                'الرصيد النقدي في نهاية الفترة': self.df['الرصيد'].iloc[-1]
            }
            
            return cash_flow_statement
    
    def generate_balance_sheet(self):
        """إنشاء الميزانية العمومية"""
        with st.spinner('🏦 جاري إنشاء الميزانية العمومية...'):
            cash_balance = self.df['الرصيد'].iloc[-1]
            income_statement = self.generate_income_statement()
            net_income = income_statement['صافي الدخل']
            
            balance_sheet = {
                'الأصول': {
                    'النقد والبنك': cash_balance,
                    'إجمالي الأصول': cash_balance
                },
                'الخصوم': {
                    'إجمالي الخصوم': 0
                },
                'حقوق الملكية': {
                    'صافي الدخل': net_income,
                    'إجمالي حقوق الملكية': net_income
                }
            }
            
            balance_sheet['الخصوم']['إجمالي الخصوم'] = cash_balance - net_income
            
            return balance_sheet
    
    def generate_expense_analysis(self):
        """تحليل المصروفات التفصيلي"""
        with st.spinner('📊 جاري إنشاء تحليل المصروفات...'):
            expense_data = self.df[self.df['مدين'] > 0].copy()
            
            if not expense_data.empty:
                expense_analysis = expense_data.groupby('الحساب المحاسبي').agg({
                    'مدين': ['sum', 'count', 'mean', 'max']
                }).round(2)
                
                expense_analysis.columns = ['إجمالي المصروفات', 'عدد الحركات', 'متوسط المبلغ', 'أعلى مبلغ']
            else:
                expense_analysis = pd.DataFrame()
            
            return expense_analysis
    
    def generate_revenue_analysis(self):
        """تحليل الإيرادات التفصيلي"""
        with st.spinner('📈 جاري إنشاء تحليل الإيرادات...'):
            revenue_data = self.df[self.df['دائن'] > 0].copy()
            
            if not revenue_data.empty:
                revenue_analysis = revenue_data.groupby('الحساب المحاسبي').agg({
                    'دائن': ['sum', 'count', 'mean', 'max']
                }).round(2)
                
                revenue_analysis.columns = ['إجمالي الإيرادات', 'عدد الحركات', 'متوسط المبلغ', 'أعلى مبلغ']
            else:
                revenue_analysis = pd.DataFrame()
            
            return revenue_analysis
    
    def generate_monthly_reports(self):
        """إنشاء تقارير شهرية"""
        with st.spinner('📅 جاري إنشاء التقارير الشهرية...'):
            monthly_data = self.df.groupby(['السنة', 'الشهر']).agg({
                'مدين': 'sum',
                'دائن': 'sum',
                'الرصيد': 'last'
            }).reset_index()
            
            monthly_data['صافي التدفق'] = monthly_data['دائن'] - monthly_data['مدين']
            
            return monthly_data

# واجهة Streamlit
def main():
    st.sidebar.title("📁 رفع الملف")
    uploaded_file = st.sidebar.file_uploader("اختر ملف كشف الحساب البنكي (Excel)", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # إنشاء النظام المحاسبي
            accounting_system = ProfessionalAccountingSystem(uploaded_file)
            
            # تصنيف الحركات
            accounting_system.classify_transactions()
            
            # إنشاء التقارير
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📖 قيود اليومية", use_container_width=True):
                    journal_entries = accounting_system.create_journal_entries()
                    st.subheader("قيود اليومية")
                    st.dataframe(journal_entries, use_container_width=True)
            
            with col2:
                if st.button("⚖️ ميزان المراجعة", use_container_width=True):
                    trial_balance = accounting_system.generate_trial_balance()
                    st.subheader("ميزان المراجعة")
                    st.dataframe(trial_balance, use_container_width=True)
            
            with col3:
                if st.button("📈 قائمة الدخل", use_container_width=True):
                    income_statement = accounting_system.generate_income_statement()
                    st.subheader("قائمة الدخل")
                    
                    # عرض قائمة الدخل بشكل جميل
                    st.metric("إجمالي الإيرادات", f"{income_statement['الإيرادات']['إجمالي الإيرادات']:,.2f} ريال")
                    st.metric("إجمالي المصروفات", f"{income_statement['المصروفات']['إجمالي المصروفات']:,.2f} ريال")
                    st.metric("صافي الدخل", f"{income_statement['صافي الدخل']:,.2f} ريال", 
                             delta=f"{income_statement['صافي الدخل']:,.2f}")
            
            col4, col5, col6 = st.columns(3)
            
            with col4:
                if st.button("💸 التدفقات النقدية", use_container_width=True):
                    cash_flow = accounting_system.generate_cash_flow_statement()
                    st.subheader("قائمة التدفقات النقدية")
                    
                    for item, value in cash_flow.items():
                        st.metric(item, f"{value:,.2f} ريال")
            
            with col5:
                if st.button("🏦 الميزانية العمومية", use_container_width=True):
                    balance_sheet = accounting_system.generate_balance_sheet()
                    st.subheader("الميزانية العمومية")
                    
                    for section, items in balance_sheet.items():
                        st.write(f"**{section}**")
                        for item, value in items.items():
                            st.metric(item, f"{value:,.2f} ريال")
            
            with col6:
                if st.button("📊 تحليل المصروفات", use_container_width=True):
                    expense_analysis = accounting_system.generate_expense_analysis()
                    st.subheader("تحليل المصروفات")
                    if not expense_analysis.empty:
                        st.dataframe(expense_analysis, use_container_width=True)
                    else:
                        st.info("لا توجد بيانات للمصروفات")
            
            # تحليل الإيرادات
            if st.button("📈 تحليل الإيرادات", use_container_width=True):
                revenue_analysis = accounting_system.generate_revenue_analysis()
                st.subheader("تحليل الإيرادات")
                if not revenue_analysis.empty:
                    st.dataframe(revenue_analysis, use_container_width=True)
                else:
                    st.info("لا توجد بيانات للإيرادات")
            
            # التقارير الشهرية
            if st.button("📅 التقارير الشهرية", use_container_width=True):
                monthly_reports = accounting_system.generate_monthly_reports()
                st.subheader("التقارير الشهرية")
                st.dataframe(monthly_reports, use_container_width=True)
            
            # ملخص سريع
            st.markdown("---")
            st.subheader("📋 الملخص السريع")
            
            income = accounting_system.generate_income_statement()
            cash_flow = accounting_system.generate_cash_flow_statement()
            balance_sheet = accounting_system.generate_balance_sheet()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💰 إجمالي الإيرادات", f"{income['الإيرادات']['إجمالي الإيرادات']:,.2f} ريال")
                st.metric("💸 إجمالي المصروفات", f"{income['المصروفات']['إجمالي المصروفات']:,.2f} ريال")
            
            with col2:
                st.metric("📈 صافي الدخل", f"{income['صافي الدخل']:,.2f} ريال")
                st.metric("🏦 الرصيد النهائي", f"{cash_flow['الرصيد النقدي في نهاية الفترة']:,.2f} ريال")
            
            with col3:
                st.metric("💳 التدفق النقدي الصافي", f"{cash_flow['صافي الزيادة (النقص) في النقد']:,.2f} ريال")
                st.metric("📊 إجمالي الأصول", f"{balance_sheet['الأصول']['إجمالي الأصول']:,.2f} ريال")
                
        except Exception as e:
            st.error(f"❌ حدث خطأ: {e}")
    
    else:
        st.info("👆 يرجى رفع ملف كشف الحساب البنكي (Excel) لبدء التحليل")
        
        st.markdown("""
        ### 📋 الميزات المتاحة:
        - 📖 قيود اليومية المحاسبية
        - ⚖️ ميزان المراجعة
        - 📈 قائمة الدخل
        - 💸 قائمة التدفقات النقدية
        - 🏦 الميزانية العمومية
        - 📊 تحليل المصروفات والإيرادات
        - 📅 تقارير شهرية
        """)

if __name__ == "__main__":
    main()
