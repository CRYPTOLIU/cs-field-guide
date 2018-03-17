import os.path
from unittest import mock
from tests.BaseTestWithDB import BaseTestWithDB
from tests.chapters.ChaptersTestDataGenerator import ChaptersTestDataGenerator
from tests.interactives.InteractivesTestDataGenerator import InteractivesTestDataGenerator
from chapters.management.commands._ChaptersLoader import ChaptersLoader
from chapters.models import Chapter
from utils.errors.MissingRequiredFieldError import MissingRequiredFieldError
from utils.errors.NoHeadingFoundInMarkdownFileError import NoHeadingFoundInMarkdownFileError
from utils.errors.EmptyMarkdownFileError import EmptyMarkdownFileError
from utils.errors.KeyNotFoundError import KeyNotFoundError


class ChaptersLoaderTest(BaseTestWithDB):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_data = ChaptersTestDataGenerator()
        self.interactives_test_data = InteractivesTestDataGenerator()
        self.loader_name = "chapters"
        self.base_path = os.path.join(self.test_data.LOADER_ASSET_PATH, self.loader_name)
        self.factory = mock.Mock()

    def test_chapters_chapter_loader_single_chapter(self):
        chapter_slug = "chapter-1"
        chapter_number = 1
        chapter_structure_file_path = os.path.join(
            self.base_path,
            chapter_slug,
            "{}.yaml".format(chapter_slug)
        )

        chapter_loader = ChaptersLoader(
            factory=self.factory,
            chapter_structure_file_path=chapter_structure_file_path,
            chapter_slug=chapter_slug,
            chapter_number=chapter_number,
            BASE_PATH=self.base_path
        )
        chapter_loader.load()

        self.assertQuerysetEqual(
            Chapter.objects.all(),
            ["<Chapter: Chapter 1>"]
        )

    def test_chapters_chapter_loader_multiple_chapters(self):
        chapter_1_slug = "chapter-1"
        chapter_1_number = 1
        chapter_1_structure_file_path = os.path.join(
            self.base_path,
            chapter_1_slug,
            "{}.yaml".format(chapter_1_slug)
        )
        chapter_loader = ChaptersLoader(
            factory=self.factory,
            chapter_structure_file_path=chapter_1_structure_file_path,
            chapter_slug=chapter_1_slug,
            chapter_number=chapter_1_number,
            BASE_PATH=self.base_path
        )
        chapter_loader.load()

        chapter_2_slug = "chapter-2"
        chapter_2_number = 2
        chapter_2_structure_file_path = os.path.join(
            self.base_path,
            chapter_2_slug,
            "{}.yaml".format(chapter_2_slug)
        )
        chapter_loader = ChaptersLoader(
            factory=self.factory,
            chapter_structure_file_path=chapter_2_structure_file_path,
            chapter_slug=chapter_2_slug,
            chapter_number=chapter_2_number,
            BASE_PATH=self.base_path
        )
        chapter_loader.load()

        self.assertQuerysetEqual(
            Chapter.objects.all(),
            [
                "<Chapter: Chapter 1>",
                "<Chapter: Chapter 2>"
            ]
        )

    def test_chapters_chapter_loader_introduction_missing_heading(self):
        chapter_slug = "missing-heading"
        chapter_number = 1
        chapter_structure_file_path = os.path.join(
            self.base_path,
            chapter_slug,
            "{}.yaml".format(chapter_slug)
        )

        chapter_loader = ChaptersLoader(
            factory=self.factory,
            chapter_structure_file_path=chapter_structure_file_path,
            chapter_slug=chapter_slug,
            chapter_number=chapter_number,
            BASE_PATH=self.base_path
        )

        self.assertRaises(
            NoHeadingFoundInMarkdownFileError,
            chapter_loader.load
        )

    def test_chapters_chapter_loader_introduction_missing_content(self):
        chapter_slug = "missing-content"
        chapter_number = 1
        chapter_structure_file_path = os.path.join(
            self.base_path,
            chapter_slug,
            "{}.yaml".format(chapter_slug)
        )

        chapter_loader = ChaptersLoader(
            factory=self.factory,
            chapter_structure_file_path=chapter_structure_file_path,
            chapter_slug=chapter_slug,
            chapter_number=chapter_number,
            BASE_PATH=self.base_path
        )
        self.assertRaises(
            EmptyMarkdownFileError,
            chapter_loader.load
        )

    def test_chapters_chapter_loader_missing_sections(self):
        chapter_slug = "missing-sections"
        chapter_number = 1
        chapter_structure_file_path = os.path.join(
            self.base_path,
            chapter_slug,
            "{}.yaml".format(chapter_slug)
        )

        chapter_loader = ChaptersLoader(
            factory=self.factory,
            chapter_structure_file_path=chapter_structure_file_path,
            chapter_slug=chapter_slug,
            chapter_number=chapter_number,
            BASE_PATH=self.base_path
        )

        self.assertRaises(
            MissingRequiredFieldError,
            chapter_loader.load
        )

    def test_chapters_chapter_loader_no_icon(self):
        chapter_slug = "no-icon"
        chapter_number = 1
        chapter_structure_file_path = os.path.join(
            self.base_path,
            chapter_slug,
            "{}.yaml".format(chapter_slug)
        )
        chapter_loader = ChaptersLoader(
            factory=self.factory,
            chapter_structure_file_path=chapter_structure_file_path,
            chapter_slug=chapter_slug,
            chapter_number=chapter_number,
            BASE_PATH=self.base_path
        )
        self.assertRaises(
            MissingRequiredFieldError,
            chapter_loader.load
        )

    @mock.patch(
        "django.contrib.staticfiles.finders.find",
        return_value=True
    )
    def test_chapters_chapter_loader_interactive(self, find_image_files):
        chapter_slug = "interactives"
        chapter_number = 1
        chapter_structure_file_path = os.path.join(
            self.base_path,
            chapter_slug,
            "{}.yaml".format(chapter_slug)
        )
        interactive1 = self.interactives_test_data.create_interactive(1)
        interactive2 = self.interactives_test_data.create_interactive(2)
        interactive3 = self.interactives_test_data.create_interactive(3)
        chapter_loader = ChaptersLoader(
            factory=self.factory,
            chapter_structure_file_path=chapter_structure_file_path,
            chapter_slug=chapter_slug,
            chapter_number=chapter_number,
            BASE_PATH=self.base_path
        )
        chapter_loader.load()
        self.assertTrue(find_image_files.called)
        self.assertQuerysetEqual(
            Chapter.objects.all(),
            ["<Chapter: Interactives>"]
        )
        self.assertEqual(
            list(Chapter.objects.get(slug=chapter_slug).interactives.order_by("slug")),
            [
                interactive1,
                interactive2,
                interactive3,
            ]
        )

    def test_chapters_chapter_loader_interactive_invalid(self):
        chapter_slug = "invalid-interactive"
        chapter_number = 1
        chapter_structure_file_path = os.path.join(
            self.base_path,
            chapter_slug,
            "{}.yaml".format(chapter_slug)
        )
        chapter_loader = ChaptersLoader(
            factory=self.factory,
            chapter_structure_file_path=chapter_structure_file_path,
            chapter_slug=chapter_slug,
            chapter_number=chapter_number,
            BASE_PATH=self.base_path
        )
        self.assertRaises(
            KeyNotFoundError,
            chapter_loader.load
        )