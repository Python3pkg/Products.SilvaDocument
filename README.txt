Copyright (c) 2002, 2003 Infrae. All rights reserved.
See also LICENSE.txt

Meta::
  
  Valid for:  Silva 0.9.3+
  Author:     Christian Zagrodnick
  Email:      cz+gocept.com
  CVS:        $Id: README.txt,v 1.3 2003/11/05 13:24:07 faassen Exp $

Silva Document

  Silva Document is an extension to Silva allowing to create structured
  documents. Silva Document formerly was part of Silva core and was factored
  out for the 0.9.3 release.
 

Editing

  The paragraphs of a Silva Document can contain markup like strong, emphasis
  or underline. When entering a paragraph with the forms based editor this
  markup needs to be represendted by some form text. Details about possible
  markup can be found in the Silva documentation[1].
  
  From Silva 0.9.2 to 0.9.3 the text markup parser has been rewritten -- it
  tries to be smart now.


  Escaping

    The intermediate solution of escaping potential markup characters
    with entities has been replaced by a more sophistiaced escaping
    mechanism. The backslash '\' is used as escaping character now:

      A **strong** text is marked up as \**strong\** in Silva.
    
    In many cases it is not possible to escape manually. The parser
    will escape anything implicitly which cannot be interpreted as
    markup, a so called conceptual escape:

      Now even a ***** (bold asterisk) is possible, or ****** two.

    But note that, once saved, all conceptual escapes will be explicit
    escapes in the edit box. This means

      our ****** two blod asterisks 

    becomes
    
      our **\**** tow bold asterisks

    if saved. 


  Links

    Links are automatically recognised and converted to a link element.


  Indexs

    Indexes do not have the `index text' part. It just [[index entry]] now.


License
  
  Silva Document is released under the BSD license. See 'LICENSE.txt'.
  

References
  
  [1] Silva documentation 
    http://infrae.com/products/silva/docs/AuthorEditorChief/ContentObject/EditTab/


