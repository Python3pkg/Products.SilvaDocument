<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
    exclude-result-prefixes="doc silva silva-content silva-extra"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:doc="http://infrae.com/namespace/silva-document"
    xmlns:silva="http://infrae.com/namespace/silva"
    xmlns:silva-extra="http://infrae.com/namespace/metadata/silva-extra"
    xmlns:silva-content="http://infrae.com/namespace/metadata/silva-content"
    version="1.0">

  <xsl:import href="silvabase:doc_elements.xslt"/>

  <xsl:output
      method="xml"
      omit-xml-declaration="yes"
      indent="no"
      doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
      doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" />

  <!-- Discard metadata and workflow information if present -->
  <xsl:template match="silva:metadata" />
  <xsl:template match="silva:workflow" />

  <xsl:template match="doc:link" mode="text-content">
    <a class="link" title="{@title}">
      <xsl:if test="@target">
        <xsl:attribute name="target">
          <xsl:value-of select="@target" />
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="@data-silva-anchor">
        <xsl:attribute name="data-silva-anchor">
          <xsl:value-of select="@data-silva-anchor" />
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="@data-silva-reference">
        <xsl:attribute name="data-silva-reference">
          <xsl:value-of select="@data-silva-reference" />
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="@data-silva-target">
        <xsl:attribute name="data-silva-target">
          <xsl:value-of select="@data-silva-target" />
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="@data-silva-href">
        <xsl:attribute name="data-silva-href">
          <xsl:value-of select="@data-silva-href" />
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates mode="text-content" />
    </a>
  </xsl:template>

  <xsl:template match="doc:image">
    <div class="image {@alignment}">
      <img src="{@rewritten_path}" alt="{@title}">
        <xsl:if test="@data-silva-reference">
          <xsl:attribute name="data-silva-reference">
            <xsl:value-of select="@data-silva-reference" />
          </xsl:attribute>
        </xsl:if>
        <xsl:if test="@data-silva-target">
          <xsl:attribute name="data-silva-target">
            <xsl:value-of select="@data-silva-target" />
          </xsl:attribute>
        </xsl:if>
        <xsl:if test="@data-silva-href">
          <xsl:attribute name="data-silva-href">
            <xsl:value-of select="@data-silva-href" />
          </xsl:attribute>
        </xsl:if>
      </img>
    </div>
  </xsl:template>

  <xsl:template match="doc:link">
    <xsl:choose>
      <xsl:when test="count(*) = 1 and count(doc:image) = 1">
        <xsl:variable name="image" select="doc:image" />
        <div class="image {$image/@alignment}">
          <a class="image-link" title="{@title}">
            <xsl:if test="@target">
              <xsl:attribute name="target">
                <xsl:value-of select="@target" />
              </xsl:attribute>
            </xsl:if>
            <xsl:if test="@data-silva-anchor">
              <xsl:attribute name="data-silva-anchor">
                <xsl:value-of select="@data-silva-anchor" />
              </xsl:attribute>
            </xsl:if>
            <xsl:if test="@data-silva-reference">
              <xsl:attribute name="data-silva-reference">
                <xsl:value-of select="@data-silva-reference" />
              </xsl:attribute>
            </xsl:if>
            <xsl:if test="@data-silva-target">
              <xsl:attribute name="data-silva-target">
                <xsl:value-of select="@data-silva-target" />
              </xsl:attribute>
            </xsl:if>
            <xsl:if test="@data-silva-href">
              <xsl:attribute name="data-silva-href">
                <xsl:value-of select="@data-silva-href" />
              </xsl:attribute>
            </xsl:if>
            <img src="{$image/@rewritten_path}" alt="{$image/@title}">
              <xsl:if test="$image/@data-silva-reference">
                <xsl:attribute name="data-silva-reference">
                  <xsl:value-of select="$image/@data-silva-reference" />
                </xsl:attribute>
              </xsl:if>
              <xsl:if test="$image/@data-silva-target">
                <xsl:attribute name="data-silva-target">
                  <xsl:value-of select="$image/@data-silva-target" />
                </xsl:attribute>
              </xsl:if>
              <xsl:if test="$image/@data-silva-href">
                <xsl:attribute name="data-silva-href">
                  <xsl:value-of select="$image/@data-silva-href" />
                </xsl:attribute>
              </xsl:if>
            </img>
          </a>
        </div>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:source">
    <div class="external-source" data-silva-name="{@id}" data-silva-settings="{@settings}">
      <xsl:apply-templates />
    </div>
  </xsl:template>

  <xsl:template match="doc:rendered_html" />

  <xsl:template match="doc:parameter" />

  <xsl:template match="/">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="doc:index" mode="text-content">
    <a class="anchor" name="{@name}" title="{@title}"></a>
  </xsl:template>

  <xsl:template match="silva:silva_document">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="doc:doc">
    <xsl:apply-templates />
  </xsl:template>

</xsl:stylesheet>
