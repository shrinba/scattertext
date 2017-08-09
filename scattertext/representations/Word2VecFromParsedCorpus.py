import itertools


from scattertext.ParsedCorpus import ParsedCorpus


class GensimPhraseAdder(object):
	def __init__(self, max_tokens_per_phrase=3, phrases = None):
		'''
		Parameters
		----------
		max_tokens_per_phrase: int, must be > 1.  Default 3
		phrases: Instance of Gensim phrases class, default None
		'''
		from gensim.models import Phrases
		self.max_tokens_per_phrase = max_tokens_per_phrase
		self.phrases = Phrases() if phrases is None else phrases

	def add_phrases(self, corpus):
		'''
		Parameters
		----------
		corpus: Corpus for phrase augmentation

		Returns
		-------
		New ParsedCorpus containing unigrams in corpus and new phrases
		'''
		assert isinstance(corpus, ParsedCorpus)
		#self.phrases.scan_vocab(CorpusAdapterForGensim.get_sentences(self.corpus))



class CorpusAdapterForGensim(object):
	@staticmethod
	def get_sentences(corpus):
		'''
		Parameters
		----------
		corpus, ParsedCorpus

		Returns
		-------
		iter: [sentence1word1, ...], [sentence2word1, ...]
		'''
		assert isinstance(corpus, ParsedCorpus)
		return itertools.chain(*[[[t.lower_ for t in sent if not t.is_punct]
		                          for sent in doc.sents]
		                         for doc in corpus.get_parsed_docs()])


class Word2VecFromParsedCorpus(object):
	def __init__(self, corpus, word2vec_model=None):
		'''
		Parameters
		----------
		corpus: ParsedCorpus from which to build word2vec model
		word2vec_model: Gensim word2vec.Word2Vec instance to be used to train word2vec model
		'''
		from gensim.models import word2vec
		assert isinstance(corpus, ParsedCorpus)
		assert word2vec_model is None or isinstance(word2vec_model, word2vec.Word2Vec)
		self.corpus = corpus
		self.model = self._get_word2vec_model(word2vec_model)

	def train(self, epochs=2000):
		'''
		Parameters
		----------
		epochs int, number of epochs to train for.  Default is 2000.

		Returns
		-------
		A trained word2vec model.
		'''

		self._scan_and_build_vocab()
		self.model.train(CorpusAdapterForGensim.get_sentences(self.corpus),
		                 total_examples=self.model.corpus_count,
		                 epochs=epochs)
		return self.model

	def _get_word2vec_model(self, word2vec_model):
		return (self._default_word2vec_model()
		        if word2vec_model is None
		        else word2vec_model)

	def _default_word2vec_model(self):
		from gensim.models import word2vec
		return word2vec.Word2Vec(size=100, alpha=0.025, window=5, min_count=5,
		                         max_vocab_size=None, sample=0, seed=1, workers=1, min_alpha=0.0001,
		                         sg=1, hs=1, negative=0, cbow_mean=0, iter=1, null_word=0,
		                         trim_rule=None, sorted_vocab=1)

	def _scan_and_build_vocab(self):
		self.model.scan_vocab(CorpusAdapterForGensim.get_sentences(self.corpus))
		self.model.build_vocab(CorpusAdapterForGensim.get_sentences(self.corpus))


class Word2VecFromParsedCorpusBigrams(Word2VecFromParsedCorpus):
	def _scan_and_build_vocab(self):
		from gensim.models import Phrases
		bigram_transformer = Phrases(CorpusAdapterForGensim.get_sentences(self.corpus))
		self.model.scan_vocab(bigram_transformer[CorpusAdapterForGensim.get_sentences(self.corpus)])
		self.model.build_vocab(bigram_transformer[CorpusAdapterForGensim.get_sentences(self.corpus)])
