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
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="silva:metadata" />

</xsl:stylesheet>
