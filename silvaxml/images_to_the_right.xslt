<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:doc="http://infrae.com/ns/silva_document"
  version="1.0">
  <xsl:output method="xml" encoding="UTF-8" />
  <xsl:strip-space elements="*" />
  <xsl:preserve-space elements="heading p pre li em strong super sub underline link" />
  
  <xsl:template match="/">
    <table>
      <tr>
        <th colspan="2">
          <xsl:apply-templates mode="metadata" />
        </th>
      </tr>
      <tr>
        <td valign="top">
          <xsl:apply-templates mode="text" />
        </td>
        <td valign="top">
          <xsl:apply-templates mode="images" />
        </td>
      </tr>
    </table>
  </xsl:template>
  
  <xsl:template match="doc:heading[@type='normal']" mode="text">
    <h3 class="heading"><xsl:apply-templates mode="text-content" /></h3>
  </xsl:template>
  
  <xsl:template match="doc:heading[@type='sub']" mode="text">
    <h4 class="heading"><xsl:apply-templates mode="text-content" /></h4>
  </xsl:template>

  <xsl:template match="doc:heading[@type='subsub']" mode="text">
    <h5 class="heading"><xsl:apply-templates mode="text-content" /></h5>
  </xsl:template>

  <xsl:template match="doc:heading[@type='paragraph']" mode="text">
    <h6 class="heading"><xsl:apply-templates mode="text-content" /></h6>
  </xsl:template>

  <xsl:template match="doc:heading[@type='subparagraph']" mode="text">
    <h6 class="minor"><xsl:apply-templates mode="text-content" /></h6>
  </xsl:template>

  <xsl:template match="doc:p[@type='normal']" mode="text">
    <p class="p"><xsl:apply-templates mode="text-content" /></p>
  </xsl:template>

  <xsl:template match="doc:p" mode="text">
    <p class="{@type}"><xsl:apply-templates mode="text-content" /></p>
  </xsl:template>

  <xsl:template match="doc:list[@type='disc']" mode="text">
    <ul class="disc">
      <xsl:apply-templates mode="list" />
    </ul>
  </xsl:template>

  <xsl:template match="doc:list[@type='square']" mode="text">
    <ul class="square">
      <xsl:apply-templates mode="list" />
    </ul>
  </xsl:template>
  
  <xsl:template match="doc:list[@type='circle']" mode="text">
    <ul class="circle">
      <xsl:apply-templates mode="list" />
    </ul>
  </xsl:template>

  <xsl:template match="doc:list[@type='1']" mode="text">
    <ol class="decimal">
      <xsl:apply-templates mode="list" />
    </ol>
  </xsl:template>

  <xsl:template match="doc:list[@type='I']" mode="text">
    <ol class="upper-roman">
      <xsl:apply-templates mode="list" />
    </ol>
  </xsl:template>
  
  <xsl:template match="doc:list[@type='i']" mode="text">
    <ol class="lower-roman">
      <xsl:apply-templates mode="list" />
    </ol>
  </xsl:template>

  <xsl:template match="doc:list[@type='A']" mode="text">
    <ol class="upper-alpha">
      <xsl:apply-templates mode="list" />
    </ol>
  </xsl:template>

  <xsl:template match="doc:list[@type='a']" mode="text">
    <ol class="lower-alpha">
      <xsl:apply-templates mode="list" />
    </ol>
  </xsl:template>
  
  <!-- need IE support? -->
  <xsl:template match="doc:list[@type='none']" mode="text">
    <ul class="nobullet">
      <xsl:apply-templates mode="list" />
    </ul>
  </xsl:template>

  <xsl:template match="doc:dlist" mode="text">
    <dl class="dl">
      <xsl:if test="@type='compact'">
        <xsl:attribute name="compact">compact</xsl:attribute>
      </xsl:if>
      <xsl:apply-templates mode="dlist" />
    </dl>
  </xsl:template>
  
  <xsl:template match="doc:pre" mode="text">
    <pre class="pre"><xsl:apply-templates mode="pre" /></pre>
  </xsl:template>
  
  <xsl:template match="doc:nlist[@type='disc']" mode="text">
    <ul class="disc">
      <xsl:apply-templates mode="nlist" />
    </ul>
  </xsl:template>
  
  <xsl:template match="doc:li" mode="list">
    <li><xsl:apply-templates mode="text-content" /></li>
  </xsl:template>
  
  <xsl:template match="doc:li" mode="nlist">
    <li>
      <xsl:apply-templates mode="text" />
    </li>
  </xsl:template>

  <xsl:template match="doc:dt" mode="dlist">
    <dt><xsl:apply-templates mode="text-content" /></dt>
  </xsl:template>

  <xsl:template match="doc:dd" mode="dlist">
    <dd><xsl:apply-templates mode="text-content" /></dd>
  </xsl:template>

  <xsl:template match="text()" mode="pre">
    <xsl:copy />
  </xsl:template>

  <xsl:template match="doc:strong" mode="text-content">
    <strong><xsl:apply-templates mode="text-content" /></strong>
  </xsl:template>

  <xsl:template match="doc:em" mode="text-content">
    <em><xsl:apply-templates mode="text-content" /></em>
  </xsl:template>
  
  <xsl:template match="doc:super" mode="text-content">
    <sup><xsl:apply-templates mode="text-content" /></sup>
  </xsl:template>
  
  <xsl:template match="doc:sub" mode="text-content">
    <sub><xsl:apply-templates mode="text-content" /></sub>
  </xsl:template>

  <xsl:template match="doc:link" mode="text-content">
    <a href="{@url}"><xsl:apply-templates mode="text-content" /></a>
  </xsl:template>

  <xsl:template match="text()" mode="images">
  </xsl:template>
  
  <xsl:template match="doc:image[@link]" mode="images">
    <a href="{@link}">
      <img src="{@path}" />
    </a>
    <br />
  </xsl:template>

  <xsl:template match="doc:image[not(@link)]" mode="images">
    <img src="{@path}" /><br />
  </xsl:template>
  
  <xsl:template match="doc:underline" mode="text-content">
    <span class="underline"><xsl:apply-templates mode="text-content" /></span>
  </xsl:template>

  <xsl:template match="doc:index">
    <a name="{@name}" />
  </xsl:template>

  <xsl:template match="doc:toc">
    <p>[a table of contents]</p>
  </xsl:template>
  
  <xsl:template match="doc:external_data">
    <p>[an external data element]</p>
  </xsl:template>
  
  <xsl:template match="doc:code">
    <p>[a code element]</p>
  </xsl:template>
  
  <xsl:template match="doc:br">
    <br />
  </xsl:template>

  <xsl:template match="doc:table">
    <table>
      <xsl:apply-templates mode="table-contents" />
    </table>
  </xsl:template>

  <xsl:template match="doc:row_heading" mode="table-contents">
    <tr valign="top">
      <th colspan="*" class="transparent"><xsl:apply-templates /></th>
    </tr>
  </xsl:template>
  
  <xsl:template match="doc:row" mode="table-contents">
    <tr>
      <xsl:apply-templates mode="tablerow-contents" />
    </tr>
  </xsl:template>

  <xsl:template match="doc:field" mode="tablerow-contents">
    <td>
      <xsl:apply-templates />
    </td>
  </xsl:template>

</xsl:stylesheet>
