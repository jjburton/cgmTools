"""
------------------------------------------
string_utils: cgm.core.lib.string_utils
Authors: David Bokser
email: dbokser@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
__MAYALOCAL = 'STRING'

import pprint
import cgm.core.cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as cgmValid

def levenshtein(s1, s2):
    '''algorithm taken from https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python '''
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def capFirst(s1):
    return "{0}{1}".format(s1[0].capitalize(),s1[1:])


def camelCase(arg = None):
    """
    """
    _str_funcName = 'camelCase'
    try:
        l_split = arg.split(' ')
        l_new = []
        _first = False
        #pprint.pprint(l_split)
        if len(l_split) == 1:
            for i,a in enumerate(l_split):
                if a and len(a)>1:
                    l_new.append(a[0].lower()+a[1:])
        else:
            for i,a in enumerate(l_split):
                if a and len(a)>1:
                    if not _first:
                        l_new.append(a)
                        _first = True
                    else:
                        l_new.append(a[0].capitalize()+a[1:])
                
        return ''.join(l_new)


    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
#>>> Utilities
#===================================================================
d_functionStringSwaps = {'.':'_attr_', ' ':'_',',':'_',
                         '+':'_add_','-':'_minus_','><':'_avg_',#pma                                                 
                         '==':'_isEqualTo_','!=':'_isNotEqualTo_','>':'_isGreaterThan_','>=':'_isGreaterOrEqualTo_','<':'_isLessThan_','<=':'_isLessThanOrEqualTo_',#condition
                         '*':'_multBy_','/':'_divBy_','^':'_pow_',}#md

def stripInvalidChars(arg = None,invalidChars = """`~!@#$%^&*()-+=[]\\{}|;':"/?><., """, noNumberStart = True,
                      functionSwap = True, replaceChar = '', cleanDoubles = True, stripTailing=True):
    """
    Modified from Hamish MacKenzie's zoo one

    :parameters:
    arg(str) - String to clean
    invalidChars(str) - Sequence of characters to remove
        noNumberStart(bool) - remove numbers at start
        functionSwap(bool) - whether to replace functions with string from dict
        replaceChar(str) - Character to use to replace with
        cleanDoubles(bool) - remove doubles
        stripTrailing(bool) - remove trailing '_'

    returns l_pos
    """
    _str_funcName = 'stripInvalidChars'
    try:
        str_Clean = cgmValid.stringArg(arg,False,_str_funcName)

        for char in invalidChars:
            if functionSwap and char in d_functionStringSwaps.keys():
                str_Clean = str_Clean.replace( char, d_functionStringSwaps.get(char) )
            else:
                str_Clean = str_Clean.replace( char, replaceChar )

        if noNumberStart:
            for n in range(10):		
                while str_Clean.startswith( str(n) ):
                    log.debug("Cleaning : %s"%str(n))
                    str_Clean = str_Clean[ 1: ]	
        if cleanDoubles and replaceChar:
            doubleChar = replaceChar + replaceChar
            while doubleChar in str_Clean:
                str_Clean = str_Clean.replace( doubleChar, replaceChar )

        if stripTailing:
            while str_Clean.endswith( '_' ):
                str_Clean = str_Clean[ :-1 ]
        return str_Clean		
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
