from mwparser import WikiMarkup
import unittest

class MWParserTests(unittest.TestCase):
    def testNothing(self):
        self.checkMarkup("", "")

    def testPre(self):
        self.checkMarkup(' this\n and\n this\nshould be preformatted',
                         '<pre>this\nand\nthis</pre><p>should be preformatted</p>')

    def testUL(self):
        self.checkMarkup("* one\n* two\n*three\n\nfour",
                        "<ul><li>one</li><li>two</li><li>three</li></ul><p>four</p>")
        
    def testBoring(self):
        self.checkMarkup("Hey there!",
                         "<p>Hey there!</p>")

    def testBasicWikiLinks(self):
        self.checkMarkup("[[Live nude lesbians]]",
                         '<p><a href="Live nude lesbians">Live nude lesbians</a></p>')

    def testEmbeddedLinks(self):
        self.checkMarkup("http://www.google.com brotha",
                         '<p><a href="http://www.google.com">http://www.google.com</a> brotha</p>')

    def testEm(self):
        self.checkMarkup("''whoa!'' zomg",
                         "<p><em>whoa!</em> zomg</p>")

    def testParagraph(self):
        self.checkMarkup("Trapped across\n\nenemy newlines",
                         "<p>Trapped across</p><p>enemy newlines</p>")

    def testOrderedList(self):
        self.checkMarkup("# one\n#two\nthree",
                         "<ol><li>one</li><li>two</li></ol><p>three</p>")

    def testBullet(self):
        self.checkMarkup("* An albino\n\nA mosquito",
                         '<ul><li>An albino</li></ul><p>A mosquito</p>')

    def testBulletWithOneNewline(self):
        self.checkMarkup("* An albino\nA mosquito",
                         '<ul><li>An albino</li></ul><p>A mosquito</p>')

    def testUnicode2utf8(self):
        # guarantee: If you pass in Unicode, you'll get utf-8 out
        self.checkMarkup(u'\x85',
                         '<p>\xc2\x85</p>')

    def testutf8safety(self):
        # guarantee: If you pass in utf-8, you'll get utf-8 back
        self.checkMarkup('\xc2\x85',
                         '<p>\xc2\x85</p>')

    def testDifficultLink(self):
        self.checkMarkup("<http://fake-domain.org/~luser+bbq/showpost.php?p=525574&postcount=7#sect>",
                         '<p>\0&lt;\0<a href="http://fake-domain.org/~luser+bbq/showpost.php?p=525574&postcount=7#sect">http://fake-domain.org/~luser+bbq/showpost.php?p=525574&postcount=7#sect</a>\0&gt;\0</p>')

    def testLabeledLink(self):
        self.checkMarkup('[http://www.google.com/ Cthuu]gle',
                         '<p><a href="http://www.google.com/">Cthuu</a>gle</p>')

    # FIXME: To pass this cleanly, we need some smarter language than strings
    # for doing HTML/XML templating.
    def testEscaping(self):
        self.checkMarkup("6 < 7 < 8",
                         "<p>6 \0&lt;\0 7 \0&lt;\0 8</p>")

    def testPre(self):
        self.checkMarkup(' zomg prefor<matted>',
                         '<pre>zomg prefor\0&lt;\0matted\0&gt;\0</pre>')

    def testSection(self):
        self.checkMarkup("== zomg ==",
                         "<h2>zomg</h2>")

    def testParagraphUlSeparation(self):
        self.checkMarkup('zqomg\n* qbbq',
                         '<p>zqomg</p><ul><li>qbbq</li></ul>')

    def testHeaderUlSeparation(self):
        self.checkMarkup('==zomg==\n* bbq\n=omg=',
                         '<h2>zomg</h2><ul><li>bbq</li></ul><h1>omg</h1>')

    def testLotsOfLinesBetweenUlAndH2(self):
        self.checkMarkup('* zomg\n\n\n==bbq==',
                         '<ul><li>zomg</li></ul><h2>bbq</h2>')

    def testComplicatedLink(self):
        self.checkMarkup('Sparta <http://www.mnot.net/sw/sparta/>',
                         '<p>Sparta \x00&lt;\x00<a href="http://www.mnot.net/sw/sparta/">http://www.mnot.net/sw/sparta/</a>\x00&gt;\x00</p>')
    def testFindReferences(self):
        markup = 'Something <ref name="foo">Something where</ref>over'
        p = WikiMarkup(markup)
        ref = p.find_references()
        self.assertEqual(ref, ['<ref name="foo">Something where</ref>'])
        got = p.render()
        self.assert_("Something where" in got)

    def testPullReferences(self):
        markup = 'Something <ref name="foo">Something where</ref>over'
        p = WikiMarkup(markup)
        ref = p.find_references(pull = True)
        self.assertEqual(ref, ['<ref name="foo">Something where</ref>'])
        got = p.render()
        self.assertEqual('<p>Something over</p>', got)

    def testLinkPrefixRendering(self):
        markup = 'foobar [[Woo]]'
        p = WikiMarkup(markup)
        p.set_link_prefix('http://www.google.com/?q=')
        got = p.render()
        self.assertEqual('<p>foobar <a href="http://www.google.com/?q=Woo">Woo</a></p>', got)

    def testNamedLinks(self):
        self.checkMarkup('[[English People|English]]', '<p><a href="English People">English</a></p>')


    def checkMarkup(self, markup, wanted):
        p = WikiMarkup(markup)
        got = p.render()
        self.assertEqual(got, wanted)



if __name__ == '__main__':
    unittest.main()
    
