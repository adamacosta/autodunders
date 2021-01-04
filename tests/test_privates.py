import autodunders


def test_obj_attrs():
	class Foo:
		a = 1
		b = 2
		def __init__(self):
			self.a = 3
			self.b = 4

	bar = Foo()

	assert autodunders._obj_attrs(bar) == ('a', 'b')
	assert autodunders._obj_attr_vals(bar) == (3, 4)

def test_cls_attrs():
	class Foo:
		a = 1
		b = 2
		def __init__(self):
			self.a = 3
			self.b = 4

	bar = Foo()

	assert autodunders._cls_attrs(bar) == ('a', 'b')
	assert autodunders._cls_attr_vals(bar) == (1, 2)
