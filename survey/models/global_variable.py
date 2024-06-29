from django.db import models
from django.utils.translation import gettext_lazy as _

class GlobalVariable(models.Model):
    number_of_responses = models.IntegerField(_("number_of_responses"),default=10)
    diagnostic_page_indexing = models.IntegerField(_("診断結果の表示の最低数"),default=20)
    download_top_number = models.IntegerField(_("Download the top results"), default=10)
    number_of_question = models.IntegerField(_("number_of_question"), default=10)

    class Meta:
        verbose_name = _("Global Variable")
        verbose_name_plural = _("Global Variables")
        permissions = (
            ("globalsetup", "Set Global Variable"),
        )

    def __str__(self):
        return "調査のグローバル設定"


