# Hackathon Team Formation Program

Here's a Python program that can form teams from your hackathon participants based on different required team compositions:

```python
import pandas as pd
import random
from collections import defaultdict

class HackathonTeamFormation:
    def __init__(self, excel_file):
        # Read the Excel file
        self.df = pd.read_excel(excel_file)
        self.participants = self.df.to_dict('records')
        
        # Group participants by role
        self.by_role = defaultdict(list)
        for p in self.participants:
            self.by_role[p['role'].lower()].append(p)
    
    def show_participant_stats(self):
        """Show statistics about available participants"""
        print("\nAvailable Participants by Role:")
        for role, people in self.by_role.items():
            print(f"{role.capitalize()}: {len(people)}")
        
        print("\nExperience Distribution:")
        print(self.df['experience'].value_counts())
        
        print("\nEvaluation Score Stats:")
        print(self.df['evaluation score'].describe())
    
    def form_teams(self, team_compositions):
        """
        Form teams based on provided compositions
        team_compositions: List of dicts specifying required roles for each team
        Example: [{'full stack': 2, 'tester': 1, 'ai engineer': 1}, ...]
        """
        teams = []
        remaining_participants = self.participants.copy()
        
        for comp in team_compositions:
            team = []
            possible = True
            
            # Try to fill each role in the composition
            for role, count in comp.items():
                role_lower = role.lower()
                available = [p for p in remaining_participants if p['role'].lower() == role_lower]
                
                if len(available) < count:
                    possible = False
                    break
                
                # Select top performers first (or random if scores are equal)
                selected = sorted(available, key=lambda x: x['evaluation score'], reverse=True)[:count]
                team.extend(selected)
                
                # Remove selected participants from remaining pool
                for p in selected:
                    remaining_participants.remove(p)
            
            if possible:
                teams.append(team)
            else:
                print(f"Could not form team with composition: {comp}. Not enough participants.")
        
        return teams, remaining_participants
    
    def print_teams(self, teams):
        """Print the formed teams in a readable format"""
        for i, team in enumerate(teams, 1):
            print(f"\nTeam {i}:")
            print("-" * 30)
            total_score = 0
            for member in team:
                print(f"{member['name']} ({member['role']}, Exp: {member['experience']}, Score: {member['evaluation score']})")
                total_score += member['evaluation score']
            avg_score = total_score / len(team) if team else 0
            print(f"\nTotal Team Score: {total_score:.1f}, Average: {avg_score:.1f}")
            print("-" * 30)
    
    def balance_teams_by_experience(self, teams):
        """Attempt to balance teams by experience levels"""
        # This is a simple approach - more sophisticated algorithms could be used
        for i in range(len(teams)):
            for j in range(i+1, len(teams)):
                # Swap members of same role if it improves balance
                for role in set([m['role'].lower() for m in teams[i] + teams[j]]):
                    members_i = [m for m in teams[i] if m['role'].lower() == role]
                    members_j = [m for m in teams[j] if m['role'].lower() == role]
                    
                    if members_i and members_j:
                        # Sort by experience to facilitate fair swaps
                        members_i.sort(key=lambda x: x['experience'])
                        members_j.sort(key=lambda x: x['experience'])
                        
                        # Swap if it reduces experience disparity
                        if abs(members_i[0]['experience'] - members_j[-1]['experience']) > 1:
                            teams[i].remove(members_i[0])
                            teams[j].remove(members_j[-1])
                            teams[i].append(members_j[-1])
                            teams[j].append(members_i[0])
        
        return teams

# Example usage
if __name__ == "__main__":
    # Initialize with your Excel file
    team_former = HackathonTeamFormation("hackathon_participants.xlsx")
    
    # Show participant statistics
    team_former.show_participant_stats()
    
    # Define your team compositions
    # Example: 4 teams with different compositions
    team_compositions = [
        {'Full Stack': 2, 'Tester': 1, 'AI Engineer': 1},  # Team 1
        {'Full Stack': 2, 'Tester': 1, 'AI Engineer': 1},  # Team 2
        {'Full Stack': 1, 'Tester': 2, 'AI Engineer': 1},  # Team 3
        {'Full Stack': 1, 'Tester': 1, 'AI Engineer': 2}   # Team 4
    ]
    
    # Form teams
    teams, remaining = team_former.form_teams(team_compositions)
    
    # Balance teams by experience
    balanced_teams = team_former.balance_teams_by_experience(teams)
    
    # Print the teams
    print("\nFormed Teams:")
    team_former.print_teams(balanced_teams)
    
    # Print remaining participants
    if remaining:
        print("\nRemaining Participants:")
        for p in remaining:
            print(f"{p['name']} ({p['role']})")
```

## How to Use This Program:

1. **Prepare Your Excel File**:
   - Ensure your Excel file has columns: name, email, phone, role, experience, evaluation score
   - Save it as "hackathon_participants.xlsx" or update the filename in the code

2. **Customize Team Compositions**:
   - Modify the `team_compositions` list in the example usage to match your desired team structures
   - Each dictionary represents one team's required roles and counts

3. **Run the Program**:
   - The program will:
     - Read participant data
     - Show statistics about available participants
     - Form teams based on your specifications
     - Attempt to balance teams by experience
     - Display the formed teams with their scores
     - Show any remaining participants who couldn't be placed

4. **Advanced Customization**:
   - You can modify the team formation logic to prioritize different criteria
   - Add additional balancing algorithms as needed

## Key Features:

- Forms teams based on specified role requirements
- Prioritizes higher evaluation scores when selecting team members
- Attempts to balance experience levels across teams
- Provides statistics about participant distribution
- Handles cases where not enough participants are available for all teams

You can extend this program further by adding GUI, more sophisticated balancing algorithms, or outputting the teams to a new Excel file.
