import autodunders
import fakemod


def test_basic():
	bar = fakemod.Foo()
	bar1 = fakemod.Foo()

	autodunders.add_dunders_to_module(fakemod)

	assert repr(bar) == 'Foo(a=1, b=2)'
	assert bar == bar1
	assert hasattr(fakemod.Foo, '__repr__') and fakemod.Foo.__repr__ is not object.__repr__

def test_add_by_str():
	bar = fakemod.Foo()
	bar1 = fakemod.Foo()

	autodunders.add_dunders_to_module('fakemod')

	assert repr(bar) == 'Foo(a=1, b=2)'
	assert bar == bar1
	assert hasattr(fakemod.Foo, '__repr__') and fakemod.Foo.__repr__ is not object.__repr__

def test_with_args():
	def custom_repr(self):
		return 'hello world'

	callbacks = {'__repr__': custom_repr}

	bar = fakemod.Foo()

	autodunders.add_dunders_to_module(fakemod, dunders=('__repr__',), callbacks=callbacks)
	assert repr(bar) == 'hello world'
