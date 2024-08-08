from smap_package.src.utils.Tool import Tool

class ToolCode(Tool):

    def __init__(self, smap_client) -> None:
        super().__init__(smap_client)
        '''
        ^^^ super() refers to the base 'Tool' template class:
              - Tool ==> smap_package/src/utils/Tool.py
              - All functions and variables defined in Tool.py are
                inherrited by tool extensions. (such as this one)
              - Standardizes the functions used by all SMAP tools 
                such as the ones below displaying the '@override' decorator
                can be found in the Tool class displaying the 
                '@abstractmethod' decorator.
              - Pre-defines the access of SMAP_Client properties such as 
                the aggregated profile spreadsheet & socr spreadsheet
              - Each tool should be provided the same instance of
                smap_client in our current approach, initialization is 
                handled by smap_client.py and new tools should be added
                to the smap_client.py script accordingly.
        '''
        '''
        ##==> Define tool level member variables here <==##
        aka: variables not intended to be accessed by other tools
        note: variables which you want to be accessible by all tools should
              be defined in smap_package/smap_client.py
            !!and their access property should be defined in Tool.py!!

        Can either initialize as None or provide a value:
          ex1: self.raw_meter_data: pd.DataFrame = None
          ex2: self.annualize: Bool = False
        '''

    @override # Decorator requires Python ver. >3.11
    def is_complete(self) -> bool:
        '''
        Performs validation whether the tool has been completed or not.

        Can either check status of outputs or instead, a 'complete' member 
        variable could be created and performed by this function.
        '''
        pass
    
    @override
    def generate_data(self, **kwargs)->None:
        '''
        The generate_data function is called by run() and is intended to
        set member variables for storing the completed data rather than
        returning anything. As you can see it returns None.

        A user will access the member variables to access output.

        Optional arguments can be used (**kwargs)
        As of SMAP 0.0.2 no functions utilize these optional arguments.
        '''
        pass

    @override
    def generate_plots(self, **kwargs)->None:
        '''
        The generate_plots function is called by run() and is intended to
        set member variables for storing the completed plots rather than
        returning anything. As you can see it returns None.

        A user will access the member variables to access plots.

        Optional arguments can be used (**kwargs)
        As of SMAP 0.0.2 no functions utilize these optional arguments.
        '''
        pass
    
    @override
    def reset(self, **kwargs):
        '''
        This function is intended to reset member variables to default values.
        '''
        pass
