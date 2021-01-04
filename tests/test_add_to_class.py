import autodunders


def test_basic_decorator():
	@autodunders.add_dunders
	class Foo:
		def __init__(self):
			self.a = 1
			self.b = 2

	bar = Foo()
	bar1 = Foo()
	assert repr(bar) == 'Foo(a=1, b=2)'
	assert bar == bar1
	assert hasattr(Foo, '__repr__') and Foo.__repr__ is not object.__repr__

def test_ne_objs():
	@autodunders.add_dunders
	class Foo:
		def __init__(self, a, b):
			self.a = a
			self.b = b

	bar = Foo(1, 2)
	bar1 = Foo(3, 4)
	assert bar != bar1
	assert bar.__repr__ is not object.__repr__

def test_ne_with_no_auto():
	@autodunders.add_dunders
	class Foo:
		def __init__(self):
			self.a = 1
			self.b = 2

	class Foo1:
		def __init__(self):
			self.a = 1
			self.b = 2

	bar = Foo()
	bar1 = Foo1()
	assert repr(bar1) != 'Foo(a=1, b=2)'
	assert bar != bar1

def test_decorator_with_args():
	def custom_repr(self):
		return 'hello world'

	callbacks = {'__repr__': custom_repr}

	@autodunders.add_dunders(dunders=('__repr__',), callbacks=callbacks)
	class Foo:
		pass

	bar = Foo()
	assert repr(bar) == 'hello world'

def test_class_attrs():
	@autodunders.add_dunders
	class Foo:
		a = 1
		b = 2
		def __init__(self):
			self.c = 3

	bar = Foo()
	assert repr(bar) == 'Foo(a=1, b=2, c=3)'

def test_obj_attrs_mask_cls_attrs():
	@autodunders.add_dunders
	class Foo:
		a = 1
		b = 2
		def __init__(self):
			self.a = 3
			self.b = 4

	bar = Foo()
	assert repr(bar) == 'Foo(a=3, b=4)'

def test_cls_with_slots():
	@autodunders.add_dunders
	class Foo:
		__slots__ = 'a', 'b'
		def __init__(self):
			self.a = 1
			self.b = 2

	bar = Foo()
	bar1 = Foo()
	assert repr(bar) == 'Foo(a=1, b=2)'
	assert bar == bar1
	assert hasattr(Foo, '__repr__') and Foo.__repr__ is not object.__repr__
