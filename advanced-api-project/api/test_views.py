import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Author, Book
from django.utils import timezone
from django.urls import reverse


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='testpass123',
            email='regular@example.com'
        )

        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='adminpass123',
            email='admin@example.com',
            is_staff=True
        )

        self.author1 = Author.objects.create(name="J.K. Rowling")
        self.author2 = Author.objects.create(name="George R.R. Martin")
        self.author3 = Author.objects.create(name="J.R.R. Tolkien")

        self.book1 = Book.objects.create(
            title="Harry Potter and the Philosopher's Stone",
            publication_year=1997,
            author=self.author1
        )
        self.book2 = Book.objects.create(
            title="Harry Potter and the Chamber of Secrets",
            publication_year=1998,
            author=self.author1
        )
        self.book3 = Book.objects.create(
            title="A Game of Thrones",
            publication_year=1996,
            author=self.author2
        )
        self.book4 = Book.objects.create(
            title="The Hobbit",
            publication_year=1937,
            author=self.author3
        )

        self.client = APIClient()

    def authenticate_user(self, user):
        self.client.force_authenticate(user=user)

    def unauthenticate(self):
        self.client.force_authenticate(user=None)


class BookCRUDTests(BaseAPITestCase):
    def test_list_books_unauthorized(self):
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('books', response.data)

    def test_create_book_unauthorized(self):
        url = reverse('book-create')
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_authorized(self):
        self.authenticate_user(self.regular_user)
        url = reverse('book-create')
        data = {
            'title': 'The Prisoner of Azkaban',
            'publication_year': 1999,
            'author': self.author1.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])
        book_count = Book.objects.filter(title=data['title']).count()
        self.assertEqual(book_count, 1)

    def test_create_book_invalid_data(self):
        self.authenticate_user(self.regular_user)
        url = reverse('book-create')
        data = {
            'title': 'Future Book',
            'publication_year': timezone.now().year + 5,
            'author': self.author1.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_book_unauthorized(self):
        url = reverse('book-detail', args=[self.book1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.book1.id)

    def test_retrieve_nonexistent_book(self):
        url = reverse('book-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_book_unauthorized(self):
        url = reverse('book-update')
        data = {
            'id': self.book1.id,
            'title': 'Updated Title',
            'publication_year': 1997,
            'author': self.author1.id
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_book_authorized(self):
        self.authenticate_user(self.regular_user)
        url = reverse('book-update')
        data = {
            'id': self.book1.id,
            'title': 'Harry Potter and the Sorcerer\'s Stone',
            'publication_year': 1997,
            'author': self.author1.id
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, data['title'])

    def test_update_book_invalid_year(self):
        self.authenticate_user(self.regular_user)
        url = reverse('book-update')
        data = {
            'id': self.book2.id,
            'title': self.book2.title,
            'publication_year': 1990,
            'author': self.author1.id
        }
        response = self.client.put(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])

    def test_delete_book_unauthorized(self):
        url = reverse('book-delete')
        data = {'id': self.book1.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_authorized(self):
        self.authenticate_user(self.regular_user)
        old_book = Book.objects.create(
            title='Old Book',
            publication_year=2000,
            author=self.author1
        )
        url = reverse('book-delete')
        data = {'id': old_book.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        book_exists = Book.objects.filter(id=old_book.id).exists()
        self.assertFalse(book_exists)

    def test_delete_recent_book(self):
        self.authenticate_user(self.regular_user)
        current_year = timezone.now().year
        recent_book = Book.objects.create(
            title='Recent Book',
            publication_year=current_year,
            author=self.author1
        )
        url = reverse('book-delete')
        data = {'id': recent_book.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        book_exists = Book.objects.filter(id=recent_book.id).exists()
        self.assertTrue(book_exists)


class AuthorCRUDTests(BaseAPITestCase):
    def test_list_authors_unauthorized(self):
        url = reverse('author-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_create_author_unauthorized(self):
        url = reverse('author-list')
        data = {'name': 'New Author'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_author_authorized(self):
        self.authenticate_user(self.regular_user)
        url = reverse('author-list')
        data = {'name': 'Stephen King'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        author_count = Author.objects.filter(name=data['name']).count()
        self.assertEqual(author_count, 1)

    def test_retrieve_author_with_books(self):
        url = reverse('author-detail', args=[self.author1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('books', response.data)

    def test_update_author_unauthorized(self):
        url = reverse('author-detail', args=[self.author1.id])
        data = {'name': 'Updated Author Name'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_author_authorized(self):
        self.authenticate_user(self.regular_user)
        url = reverse('author-detail', args=[self.author1.id])
        data = {'name': 'J. K. Rowling'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.name, data['name'])

    def test_delete_author_unauthorized(self):
        url = reverse('author-detail', args=[self.author1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_author_authorized(self):
        self.authenticate_user(self.regular_user)
        new_author = Author.objects.create(name='Test Author to Delete')
        url = reverse('author-detail', args=[new_author.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        author_exists = Author.objects.filter(id=new_author.id).exists()
        self.assertFalse(author_exists)


class FilteringSearchingOrderingTests(BaseAPITestCase):
    def test_filter_by_title(self):
        url = reverse('book-list') + '?title=harry'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = response.data['books']
        self.assertEqual(len(books), 2)

    def test_filter_by_author_id(self):
        url = reverse('book-list') + f'?author={self.author1.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = response.data['books']
        self.assertEqual(len(books), 2)

    def test_filter_by_publication_year(self):
        url = reverse('book-list') + '?publication_year=1997'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = response.data['books']
        self.assertEqual(len(books), 1)

    def test_filter_by_year_range(self):
        url = reverse('book-list') + '?publication_year__gte=1990&publication_year__lte=2000'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = response.data['books']
        self.assertEqual(len(books), 3)

    def test_search_functionality(self):
        url = reverse('book-list') + '?search=potter'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = response.data['books']
        self.assertEqual(len(books), 2)

    def test_ordering_by_title(self):
        url = reverse('book-list') + '?ordering=title'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = response.data['books']
        if len(books) >= 2:
            titles = [book['title'] for book in books]
            self.assertEqual(titles, sorted(titles))

    def test_ordering_by_publication_year(self):
        url = reverse('book-list') + '?ordering=publication_year'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = response.data['books']
        if len(books) >= 2:
            years = [book['publication_year'] for book in books]
            self.assertEqual(years, sorted(years))

    def test_combined_filter_search_order(self):
        url = reverse('book-list') + '?author=1&search=harry&ordering=-publication_year'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = response.data['books']
        self.assertEqual(len(books), 2)

    def test_books_by_author_view(self):
        url = reverse('books-by-author', args=[self.author3.id]) + '?ordering=title'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['author'], self.author3.name)

    def test_response_metadata_includes_filters(self):
        url = reverse('book-list') + '?title=harry&search=chamber&ordering=-year'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('filters_applied', response.data)
        self.assertIn('total_count', response.data)


class PaginationTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        for i in range(15):
            Book.objects.create(
                title=f"Test Book {i}",
                publication_year=2000 + i,
                author=self.author1
            )

    def test_pagination_default(self):
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

    def test_pagination_with_page_parameter(self):
        url = reverse('book-list') + '?page=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_pagination_with_custom_page_size(self):
        url = reverse('book-list') + '?page_size=5'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)


class AuthenticationPermissionTests(BaseAPITestCase):
    def test_token_authentication(self):
        url = reverse('book-create')
        data = {
            'title': 'Test Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_session_authentication(self):
        url = reverse('book-create')
        data = {
            'title': 'Session Auth Book',
            'publication_year': 2023,
            'author': self.author1.id
        }

        # Test without login - should fail
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test with login - should succeed
        login_success = self.client.login(username='regular_user', password='testpass123')
        self.assertTrue(login_success)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Logout
        self.client.logout()

    def test_different_user_permissions(self):
        self.authenticate_user(self.regular_user)
        url = reverse('book-create')
        data = {
            'title': 'Regular User Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.authenticate_user(self.admin_user)
        url = reverse('book-create')
        data = {
            'title': 'Admin User Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)