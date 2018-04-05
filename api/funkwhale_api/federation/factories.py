import factory
import requests
import requests_http_signature

from django.utils import timezone

from funkwhale_api.factories import registry

from . import keys
from . import models


registry.register(keys.get_key_pair, name='federation.KeyPair')


@registry.register(name='federation.SignatureAuth')
class SignatureAuthFactory(factory.Factory):
    algorithm = 'rsa-sha256'
    key = factory.LazyFunction(lambda: keys.get_key_pair()[0])
    key_id = factory.Faker('url')
    use_auth_header = False
    headers = [
        '(request-target)',
        'user-agent',
        'host',
        'date',
        'content-type',]
    class Meta:
        model = requests_http_signature.HTTPSignatureAuth


@registry.register(name='federation.SignedRequest')
class SignedRequestFactory(factory.Factory):
    url = factory.Faker('url')
    method = 'get'
    auth = factory.SubFactory(SignatureAuthFactory)

    class Meta:
        model = requests.Request

    @factory.post_generation
    def headers(self, create, extracted, **kwargs):
        default_headers = {
            'User-Agent': 'Test',
            'Host': 'test.host',
            'Date': 'Right now',
            'Content-Type': 'application/activity+json'
        }
        if extracted:
            default_headers.update(extracted)
        self.headers.update(default_headers)


@registry.register
class ActorFactory(factory.DjangoModelFactory):

    public_key = None
    private_key = None
    preferred_username = factory.Faker('user_name')
    summary = factory.Faker('paragraph')
    domain = factory.Faker('domain_name')
    url = factory.LazyAttribute(lambda o: 'https://{}/users/{}'.format(o.domain, o.preferred_username))
    inbox_url = factory.LazyAttribute(lambda o: 'https://{}/users/{}/inbox'.format(o.domain, o.preferred_username))
    outbox_url = factory.LazyAttribute(lambda o: 'https://{}/users/{}/outbox'.format(o.domain, o.preferred_username))

    class Meta:
        model = models.Actor

    @classmethod
    def _generate(cls, create, attrs):
        has_public = attrs.get('public_key') is not None
        has_private = attrs.get('private_key') is not None
        if not has_public and not has_private:
            private, public = keys.get_key_pair()
            attrs['private_key'] = private.decode('utf-8')
            attrs['public_key'] = public.decode('utf-8')
        return super()._generate(create, attrs)


@registry.register(name='federation.Note')
class NoteFactory(factory.Factory):
    type = 'Note'
    id = factory.Faker('url')
    published = factory.LazyFunction(
        lambda: timezone.now().isoformat()
    )
    inReplyTo = None
    content = factory.Faker('sentence')

    class Meta:
        model = dict