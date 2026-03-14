from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Account, Transaction


class FinanceFlowTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='joel', password='secret123!')

	def test_register_creates_account_and_allows_login(self):
		response = self.client.post(
			reverse('register'),
			{
				'username': 'newuser',
				'password1': 'Password123##',
				'password2': 'Password123##',
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		created_user = User.objects.get(username='newuser')
		self.assertTrue(Account.objects.filter(user=created_user).exists())

	def test_create_expense_and_loan_transactions(self):
		self.client.login(username='joel', password='secret123!')

		expense_response = self.client.post(
			reverse('expenses'),
			{
				'name': 'Transport',
				'amount': '25000',
				'due_date': '2026-03-14',
				'notes': 'Taxi rides',
			},
			follow=True,
		)
		self.assertEqual(expense_response.status_code, 200)

		loan_response = self.client.post(
			reverse('loans'),
			{
				'name': 'Business Loan',
				'amount': '500000',
				'interest_rate': '7.5',
				'due_date': '2026-06-30',
				'notes': 'Quarterly installment',
			},
			follow=True,
		)
		self.assertEqual(loan_response.status_code, 200)

		account = Account.objects.get(user=self.user)
		self.assertEqual(account.transactions.count(), 2)
		self.assertEqual(account.transactions.expenses().count(), 1)
		self.assertEqual(account.transactions.loans().count(), 1)
		self.assertTrue(
			Transaction.objects.filter(account=account, kind=Transaction.Kind.LOAN, name='Business Loan').exists()
		)


class FinanceApiTests(TestCase):
	def test_register_login_and_create_expense(self):
		register_response = self.client.post(
			reverse('api-register'),
			{
				'username': 'mobileuser',
				'password': 'StrongPass123!',
			},
		)
		self.assertEqual(register_response.status_code, 201)

		login_response = self.client.post(
			reverse('api-login'),
			{
				'username': 'mobileuser',
				'password': 'StrongPass123!',
			},
		)
		self.assertEqual(login_response.status_code, 200)
		token = login_response.json()['access']

		headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

		expense_response = self.client.post(
			reverse('api-expenses'),
			{
				'name': 'Data bundles',
				'amount': '12000',
				'due_date': '2026-03-14',
				'notes': 'Weekly internet',
			},
			**headers,
		)
		self.assertEqual(expense_response.status_code, 201)
		self.assertEqual(expense_response.json()['kind'], Transaction.Kind.EXPENSE)

		categories_response = self.client.get(reverse('api-categories'), **headers)
		self.assertEqual(categories_response.status_code, 200)
		self.assertGreater(len(categories_response.json()), 0)

		income_response = self.client.post(
			reverse('api-income'),
			{
				'name': 'Monthly Salary',
				'amount': '1200000',
				'due_date': '2026-03-10',
				'notes': 'March payroll',
			},
			**headers,
		)
		self.assertEqual(income_response.status_code, 201)
		self.assertEqual(income_response.json()['kind'], Transaction.Kind.INCOME)

		loan_response = self.client.post(
			reverse('api-loans'),
			{
				'name': 'Emergency Loan',
				'amount': '300000',
				'interest_rate': '5.0',
				'due_date': '2026-06-01',
				'notes': 'Unexpected costs',
			},
			**headers,
		)
		self.assertEqual(loan_response.status_code, 201)
		self.assertEqual(loan_response.json()['kind'], Transaction.Kind.LOAN)

		sync_response = self.client.post(
			reverse('api-sync'),
			{
				'expenses': [
					{
						'name': 'Market',
						'amount': '45000',
						'due_date': '2026-03-15',
						'notes': 'Weekly food',
					}
				],
				'incomes': [
					{
						'name': 'Farm Sale',
						'amount': '600000',
						'due_date': '2026-03-16',
						'notes': 'Maize sale',
					}
				],
				'loans': [
					{
						'name': 'Supplier Credit',
						'amount': '200000',
						'interest_rate': '3.5',
						'due_date': '2026-07-01',
						'notes': 'Inventory top up',
					}
				],
			},
			content_type='application/json',
			**headers,
		)
		self.assertEqual(sync_response.status_code, 200)
		self.assertEqual(sync_response.json()['synced_expenses'], 1)
		self.assertEqual(sync_response.json()['synced_incomes'], 1)
		self.assertEqual(sync_response.json()['synced_loans'], 1)

		created_user = User.objects.get(username='mobileuser')
		account = Account.objects.get(user=created_user)
		self.assertEqual(account.transactions.expenses().count(), 2)
		self.assertEqual(account.transactions.incomes().count(), 2)
		self.assertEqual(account.transactions.loans().count(), 2)

		monthly_report = self.client.get(reverse('api-report-monthly'), {'year': 2026, 'month': 3}, **headers)
		self.assertEqual(monthly_report.status_code, 200)
		self.assertIn('total_income', monthly_report.json())

		trend_report = self.client.get(reverse('api-report-trends'), **headers)
		self.assertEqual(trend_report.status_code, 200)
		self.assertIn('trends', trend_report.json())

		receipt_file = SimpleUploadedFile('receipt.txt', b'receipt content', content_type='text/plain')
		receipt_response = self.client.post(
			reverse('api-receipts'),
			{
				'transaction': expense_response.json()['id'],
				'file': receipt_file,
			},
			**headers,
		)
		self.assertEqual(receipt_response.status_code, 201)

		fcm_response = self.client.post(
			reverse('api-fcm-register'),
			{
				'token': 'device-token-123',
				'device_name': 'Pixel 7',
				'is_active': True,
			},
			content_type='application/json',
			**headers,
		)
		self.assertEqual(fcm_response.status_code, 201)

		sms_response = self.client.post(
			reverse('api-sms-parse'),
			{
				'sms': 'You have sent UGX 15,000 to John Doe. Transaction ID: MTN20260313.',
			},
			content_type='application/json',
			**headers,
		)
		self.assertEqual(sms_response.status_code, 200)
		self.assertTrue(sms_response.json()['parsed'])

		dashboard_response = self.client.get(reverse('api-dashboard'), **headers)
		self.assertEqual(dashboard_response.status_code, 200)
		self.assertIn('totals', dashboard_response.json())
