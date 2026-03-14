from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

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
