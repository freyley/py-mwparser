# Learning unit testing from http://www.onlamp.com/pub/a/python/2004/12/02/tdd_pyunit.html

# Nested lists!  Especially nested <ul>s, but nested <ul> in <ol> and vice versa is great too
import re
import unittest

def find_lists(start_marker, tag, para):
    ''' Input: A bunch of junk
    Output: None if no modification done,
    otherwise return (formatted_line, unformatted_remainder) '''
    unformatted_remainder = ''
    ret = ''
    assert '<' not in tag and '>' not in tag, "sample tag is 'ol'"
    assert len(start_marker) == 1, "This code assumes start_marker's length is 1"
    # look for a list
    if para.strip() and para[0] == start_marker:
        # then it's a list entry
        ul = ''
        maybe_lis = para.split('\n')
        while maybe_lis:
            maybe_li = maybe_lis[0]
            if maybe_li and maybe_li[0] == start_marker:
                # FIXME: What's the right behavior for nesting
                # lists?  <ul><li><ul><li>?  Do I need to be aware
                # of nesting between paras?
                li = maybe_li[1:].strip()
                ul += "<li>" + li + "</li>"
                maybe_lis = maybe_lis[1:]
            else:
                unformatted_remainder += '\n'.join(maybe_lis)
                maybe_lis = []
        ret += '<%s>' % tag + ul + '</%s>' % tag
        return (ret, unformatted_remainder)

def handle_section(s):
    ''' Input: some string
    Output: None if no modification done,
    otherwise return (formatted_line, unformatted_remainder) '''
    useful = False
    if '\n' not in s:
        s += '\n' # Evil :-)
    firstline, rest = s.split('\n', 1)
    equals, chomped = chomp_equals(firstline)
    if 1 <= equals <= 5:
        useful = True
        firstline = '<h%d>%s</h%d>' % (equals, chomped, equals)
    if useful:
        return (firstline, rest)

def chomp_equals(s):
    ''' Input: == zomg ==,
    Output: (2, "zomg")'''
    chomped = s
    equals = 0
    while chomped and (chomped[0] == chomped[-1] == '='):
        chomped = chomped[1:-1]
        equals += 1
    return (equals, chomped.strip())

class WikiMarkup:
    urlregex = r"http://([\w./+\-=&#~?]*)"
    
    def __init__(self, s = ''):
        self.link_prefix = ''
        self.set_markup(s)
    
    def set_link_prefix(self, prefix):
        self.link_prefix = prefix
    
    def find_references(self, pull=False):
        ref_re = r'<ref.*</ref>'
        results = re.findall(ref_re, self.s)
        if pull:
            self.s = re.sub(ref_re, '', self.s)
        return results

    def _replace_angle_brackets(self):
        self.s = self.s.replace('<', '\0&lt;\0') # Padded with \0 to prevent
        self.s = self.s.replace('>', '\0&gt;\0') # their accidental splitting.
    def set_markup(self, s):
        if type(s) == unicode:
            self.s = s
        else:
            self.s = unicode(s, 'utf-8')
        
    def render(self):
        self._replace_angle_brackets()

        ret = ""
        paragraphs = re.split(r'\n', self.s) # That's right, eat that whitespace
        while paragraphs:
            para = paragraphs.pop(0)
            # check for '\n\n' condition, too
            grow_more = True
            while paragraphs and grow_more:
                # check for \n\n condition
                if para.strip() == '' and paragraphs[0].strip() == '':
                    grow_more = False
                    break
                # Good, so now we check if the next paragraph is of the same type as this one
                # if so, slurp it in
                for fn in handle_section, lambda s: find_lists('*', 'ul', s), \
                    lambda s: find_lists('#', 'ol', s):
                    if fn(para):
                        if fn(paragraphs[0]):
                            para += '\n' + paragraphs.pop(0)
                            break
                    
                else:
                    grow_more = False
            para = re.sub(r"''(.*?)''", r"<em>\1</em>", para)
            # square bracket links
            # First look for ]
            newpara = '' # Grow into here

            # First look for ]]
            subsplitted = para.split(']]')
            for subelt in subsplitted:
                internal = re.sub(r"\[\[(.*)", r'<a href="%s\1">\1</a>' % self.link_prefix, subelt)
                if internal != subelt:
                    newpara += internal
                else:
                    splitted = subelt.split(']')
                    # Run regex sub on elements
                    namedlinkre = r'\[' + self.urlregex + ' ' + r'(.+)'
                    for elt in splitted:
                        named = re.sub(namedlinkre, r'<a href="http://\1">\2</a>', elt)
                        if named != elt:
                            newpara += named
                        else: # if no change
                            linked = re.sub(self.urlregex, r'<a href="http://\1">http://\1</a>', elt)
                            newpara += linked
                            if not (elt is splitted[-1]): # FIXME: "is" check is wrong for ''
                                newpara += ']'
            para = newpara
            # look for section-ness
            hope = handle_section(para)
            if hope:
                formatted, remainder = hope
                ret += formatted
                if hope:
                    para = '' # clear para so nothing later touches it
                    paragraphs.insert(0, remainder)
            # look for ULs
            hope = find_lists('*', 'ul', para)
            if hope:
                formatted, remainder = hope
                ret += formatted
                if hope:
                    para = ''
                    paragraphs.insert(0, remainder)

            # look for OLs
            hope = find_lists('#', 'ol', para)
            if hope:
                formatted, remainder = hope
                ret += formatted
                if hope:
                    para = ''
                    paragraphs.insert(0, remainder)

            # look for a PRE
            if para.strip() and para[0] == ' ':
                pre_so_far = []
                maybe_pres = para.split('\n')
                while maybe_pres:
                    maybe_pre = maybe_pres[0]
                    if maybe_pre and maybe_pre[0] == ' ':
                        pre = maybe_pre[1:]
                        pre_so_far.append(pre)
                        maybe_pres = maybe_pres[1:]
                    else:
                        paragraphs.insert(0, '\n'.join(maybe_pres))
                        maybe_pres = []
                ret += '<pre>' + '\n'.join(pre_so_far) + '</pre>'
                para = ''
            # otherwise
            if para:
                ret += '<p>' + para + '</p>'

        return ret.encode('utf-8')


