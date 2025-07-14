from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Article, ArticleXml, Author
from .scripts import fetch, format
# Q module
from django.db.models import Q


# signal used to create article object when xml file is uploaded
@receiver(post_save, sender=ArticleXml)
def create_article(sender, instance, created, **kwargs):
    if created:
        # Fetch data from XML file
        data = fetch(instance.xml_file.path)
        # Format data
        data = format(data)
        # creating authors and adding them to the article, if the data is empty or '' then it will be set to None
        article = Article.objects.get_or_create(
            url_id=data['url_id'] if data['url_id'] != '' else None,
            title=data['title'] if data['title'] != '' else None,
            genre=data['genre'] if data['genre'] != '' else None,
            date_published=data['date_published'] if data['date_published'] != '' else None,
            doi_id=data['doi_id'] if data['doi_id'] != '' else None,
            abstract=data['abstract'] if data['abstract'] != '' else None,
            # if keywords is in list then join them with comma and if already in string then just set it to string
            keywords=', '.join(data['keywords']) if type(
                data['keywords']) == list else data['keywords'] if data['keywords'] != '' else None,
            discipline=', '.join(data['discipline']) if type(
                data['discipline']) == list else data['discipline'] if data['discipline'] != '' else None,
            submission_id=data['submission_id'] if data['submission_id'] != '' else None,
            volume=data['volume'] if data['volume'] != '' else None,
            number=data['number'] if data['number'] != '' else None,
            year=data['year'] if data['year'] != '' else None,
            pages=data['pages'] if data['pages'] != '' else None
        )
        if data['authors'] != '':
            authors = data['authors']
            for author in authors:
                # get only with name  or create new author
                author = Author.objects.get_or_create(
                    given_name=author['given_name'] if author['given_name'] != '' else None,
                    family_name=author['family_name'] if author['family_name'] != '' else None,
                    affiliation=author['affiliation'] if author['affiliation'] != '' else None,
                    country=author['country'] if author['country'] != '' else None,
                    email=author['email'] if author['email'] != '' else None,
                    bio=author['bio'] if author['bio'] != '' else None
                )
                article[0].authors.add(author[0])
        else:
            article[0].authors.add(None)
        # update the instance object name with article title
        instance.article_name = article[0].title
        article[0].save()
        instance.save()


# signal used to delete author object when article object is deleted
@receiver(pre_delete, sender=Article)
def delete_article(sender, instance, **kwargs):
    instance.authors.all().delete()


# signal used to delete xml file when xml object is deleted
@receiver(pre_delete, sender=ArticleXml)
def delete_xml(sender, instance, **kwargs):
    instance.xml_file.delete()
