{% load i18n %}

{% blocktrans with title=content.title %}

Bonjour,

La bêta de **{{ title }}** a été mise à jour.

-> [Lien de la bêta : {{ title }}]({{ url }}) <-

Merci d'avance pour vos relectures et commentaires.

{%  endblocktrans %}
