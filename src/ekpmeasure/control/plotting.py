from IPython import display

__all__ = ('update_plot', )

def update_plot(fig):
    """Interactively update fig in Jupyter notebook.
    
    args:
        fig (matplotlib.figure.Figure): updated figure to replot
    """
    display.display(fig)
    display.clear_output(wait=True)
    return 