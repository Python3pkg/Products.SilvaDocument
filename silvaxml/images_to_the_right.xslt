<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet 
  exclude-result-prefixes="doc silva"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:doc="http://infrae.com/ns/silva_document"
  xmlns:silva="http://www.infrae.com/xml"
  version="1.0">
  <xsl:output method="xml" encoding="UTF-8" />

  <xsl:import href="doc_elements.xslt"/>
  
  <xsl:template match="/">
    <xsl:apply-templates />
  </xsl:template>
  
  <xsl:template match="silva_document">
    <xsl:apply-templates />
  </xsl:template>
  
  <xsl:template match="doc:doc">
    <table>
      <tr>
        <td valign="top">
          <xsl:apply-templates/>
        </td>
        <td valign="top">
          <xsl:apply-templates mode="images" />
        </td>
      </tr>
    </table>
  </xsl:template>
  
  <xsl:template match="silva:metadata" />
  
  <xsl:template match="doc:image" />
          
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

</xsl:stylesheet>
