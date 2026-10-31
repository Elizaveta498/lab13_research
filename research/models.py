from django.db import models

class Research(models.Model):

    STATUS_CHOICES = [
        ('planned', 'Запланировано'),
        ('ongoing', 'В процессе'),
        ('completed', 'Завершено'),
        ('published', 'Опубликовано'),
    ]

    title = models.CharField(max_length=255, verbose_name='Название исследования')
    author = models.CharField(max_length=255, verbose_name='Автор/руководитель')
    field = models.CharField(max_length=255, verbose_name='Область науки')
    description = models.TextField(verbose_name='Описание')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='planned', verbose_name='Статус',
    )
    budget = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name='Бюджет',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Научное исследование'
        verbose_name_plural = 'Научные исследования'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author', 'start_date'],
                name='unique_research'
            )
        ]

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'field': self.field,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'budget': str(self.budget),
            'created_at': self.created_at.isoformat(),
        }