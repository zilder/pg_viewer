#coding: utf-8
import urwid
import psycopg2

_con = None

class MainWindow(urwid.Frame):
	def __init__(self):
		self.tables_list_walker = urwid.SimpleFocusListWalker([urwid.Text('tables')])
		self.left = urwid.LineBox(urwid.BoxAdapter(urwid.ListBox(self.tables_list_walker), 22))
		self.right_text = urwid.Text('Select table to view it\'s structure')
		self.right = urwid.LineBox(self.right_text)
		self._create_columns()

		header = urwid.Text("Postgres view")
		header = urwid.AttrWrap(header,'header')

		self.frame = urwid.AttrMap(urwid.Frame(self._create_columns(), header=header), 'basic');

	def get_widget(self):
		return self.frame

	def _create_columns(self):
		self.columns = urwid.Columns([('fixed', 24, self.left), self.right])
		walker = urwid.SimpleListWalker([self.columns])
		listbox = urwid.ListBox(walker)	
		return listbox
	
	def set_tables_list(self, tables):
		result = []
		for t in tables:
			button = urwid.Button(t)
			urwid.connect_signal(button, 'click', table_button_clicked, self)
			result.append(urwid.AttrMap(button, None, focus_map='selected'))

		self.tables_list_walker[:] = result 

def table_button_clicked(button, wnd):
	con = get_connection()
	cur = con.cursor()
	cur.execute('select attname, atttypid::regtype from pg_attribute where attnum > 0 and attrelid = %s::regclass', (button.label,))

	result = '%s\n\n' % button.label
	for r in cur.fetchall():
		result += '%s   (%s)\n' % (r[0], r[1])
	wnd.right_text.set_text(result)

def main():
	con = get_connection()
	cur = con.cursor()
	cur.execute("select tablename from pg_tables where schemaname = 'public'");

	single_color = [('basic', 'white', 'black'), ('selected', 'white', 'dark red'), ('header', 'white', 'dark green')]

	wnd = MainWindow()
	wnd.set_tables_list([r[0] for r in cur.fetchall()])
	loop = urwid.MainLoop(wnd.get_widget(), palette=single_color)
	loop.run()

def get_connection():
	global _con
	if not _con:
		_con = psycopg2.connect('dbname=postgres user=zilder')
	return _con;
	
if __name__ == '__main__':
	main()

