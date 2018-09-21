import re
import yaml

class Hash(yaml.YAMLObject):
	yaml_tag = u'!Hash'

	digest_re = re.compile(r'^[0-9a-f]{96}$')

	def __init__(self, digest):
		self.Digest = digest

	def __repr__(self):
		return "%s(Digest=%r)" % (
			self.__class__.__name__, self.Digest
		)

	def validate(self):
		if not hasattr(self, 'Digest'):
			raise RuntimeError("No 'Digest' attribute.")
		if not isinstance(self.Digest, str):
			raise RuntimeError("'Digest' has to be string.")
		if len(self.Digest) != 96:
			raise RuntimeError("'Digest' has to be string of length 96 (is {}).".format(len(self.Digest)))
		if self.digest_re.match(self.Digest) is None:
			raise RuntimeError("'Digest: {}' has an incorrect format.".format(self.Digest))

		keys = set(self.__dict__.keys())
		keys.remove('Digest')
		if len(keys) > 0:
			raise RuntimeError("Unknown attributes provided: {}".format(', '.join(keys)))
